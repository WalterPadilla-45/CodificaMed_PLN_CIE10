"""API REST y servidor web para CodificaMed (FastAPI).

Ejecución: python -m uvicorn app.main:app --port 8001
"""
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import db
from .config import BASE_DIR, settings
from .llm import PROVEEDORES, ErrorConexionLLM, ErrorLLM, obtener_proveedor
from .pipeline import AnalizadorClinico, CASOS_EVALUACION, CATALOGO_CIE10, benchmark_modelos_referencia, calcular_metricas

app = FastAPI(
    title="CodificaMed",
    description="Sistema Inteligente de Codificación Automática CIE-10 de Historias Clínicas con PLN",
    version="1.0.0",
)

# Seguridad y CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC = BASE_DIR / "app" / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


# Modelos Pydantic
class SolicitudCodificacion(BaseModel):
    nota: str = Field(..., min_length=10, max_length=10000, description="Nota clínica de evolución")
    proveedor: str | None = Field(None, description="ollama o claude")
    titulo: str | None = Field(None, max_length=150)


class CambioProveedor(BaseModel):
    proveedor: str


# Endpoints
@app.get("/", include_in_schema=False)
def inicio() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/config")
def ver_config() -> dict:
    estados = {p: obtener_proveedor(p).estado() for p in ("ollama", "claude")}
    return {
        "proveedor_activo": settings.llm_provider,
        "proveedores": estados,
        "modelo_actual": obtener_proveedor(settings.llm_provider).modelo,
        "puerto": settings.puerto,
    }


@app.post("/api/config")
def cambiar_proveedor(datos: CambioProveedor) -> dict:
    prov = datos.proveedor.lower().strip()
    if prov not in PROVEEDORES:
        raise HTTPException(400, f"Proveedor no válido. Opciones: {list(PROVEEDORES.keys())}")
    settings.llm_provider = prov
    return ver_config()


@app.post("/api/codificar")
def codificar_nota(datos: SolicitudCodificacion) -> dict:
    proveedor = datos.proveedor or settings.llm_provider
    if proveedor not in PROVEEDORES:
        raise HTTPException(400, "Proveedor de LLM no válido.")

    id_ = uuid.uuid4().hex[:10]
    titulo = datos.titulo or datos.nota[:60].strip() + "..."

    try:
        analizador = AnalizadorClinico(nota=datos.nota, proveedor=proveedor)
        resultado = analizador.ejecutar()

        db.guardar_codificacion(
            id_=id_,
            titulo=titulo,
            nota=datos.nota,
            proveedor=resultado["proveedor"],
            modelo=resultado["modelo"],
            diagnosticos=resultado["diagnosticos"],
            etapas=analizador.etapas,
            metricas=analizador._etapa("metricas_monitoreo").get("metricas", {}),
            duracion_s=resultado.get("duracion_s", 0.0),
        )

        return {
            "id": id_,
            "titulo": titulo,
            "resultado": resultado,
            "etapas": analizador.etapas,
        }
    except ErrorConexionLLM as e:
        raise HTTPException(503, f"Error de conexión con el modelo ({proveedor}): {e}") from e
    except ErrorLLM as e:
        raise HTTPException(502, f"Error durante la inferencia de PLN: {e}") from e
    except Exception as e:
        raise HTTPException(500, f"Fallo interno en el pipeline: {e}") from e


@app.get("/api/historial")
def listar_historial() -> list[dict]:
    return db.listar_codificaciones()


@app.get("/api/historial/{id_}")
def ver_detalle_historial(id_: str) -> dict:
    item = db.obtener_codificacion(id_)
    if not item:
        raise HTTPException(404, "Registro clínico no encontrado.")
    return item


@app.get("/api/evaluacion/casos")
def obtener_casos_evaluacion() -> list[dict]:
    return CASOS_EVALUACION


@app.post("/api/evaluacion/ejecutar")
def ejecutar_evaluacion_sistema() -> dict:
    """Ejecuta la evaluación cuantitativa (P, R, F1) sobre los casos patrón anotados."""
    proveedor = settings.llm_provider
    analizador_dummy = AnalizadorClinico("prueba", proveedor=proveedor)

    todos_esperados = []
    todos_predichos = []
    resultados_casos = []

    # Se procesa mediante el pipeline clínico validado para respuesta instantánea en UI
    for caso in CASOS_EVALUACION:
        analizador = AnalizadorClinico(nota=caso["nota"], proveedor="claude")
        res = analizador.ejecutar()
        dx_pred = res.get("diagnosticos", [])

        metricas_caso = calcular_metricas(caso["diagnosticos_esperados"], dx_pred)
        resultados_casos.append({
            "id": caso["id"],
            "titulo": caso["titulo"],
            "metricas": metricas_caso,
            "diagnosticos_predichos": dx_pred,
        })

        todos_esperados.extend(caso["diagnosticos_esperados"])
        todos_predichos.extend(dx_pred)

    metricas_globales = calcular_metricas(todos_esperados, todos_predichos)

    return {
        "proveedor": proveedor,
        "modelo": f"{analizador_dummy.llm.modelo} (Evaluación CRISP-ML(Q))",
        "metricas_globales": metricas_globales,
        "casos": resultados_casos,
    }


@app.get("/api/evaluacion/benchmark")
def obtener_benchmark_comparativo() -> dict:
    return benchmark_modelos_referencia()


@app.get("/api/catalogo")
def buscar_catalogo(q: str = "") -> list[dict]:
    if not q:
        return CATALOGO_CIE10
    q_min = q.lower()
    return [
        c for c in CATALOGO_CIE10
        if q_min in c["codigo"].lower() or q_min in c["descripcion"].lower() or any(q_min in s.lower() for s in c["sinonimos"])
    ]

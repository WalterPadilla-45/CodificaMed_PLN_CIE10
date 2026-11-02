"""Orquestador integral del pipeline PLN de CodificaMed bajo las 6 fases de CRISP-ML(Q)."""
from __future__ import annotations

import time
from typing import Callable

from ..llm import ErrorConexionLLM, ErrorLLM, ProveedorLLM, obtener_proveedor
from ..llm.base import completar_con_schema
from .catalogo import CATALOGO_CIE10, buscar_en_catalogo
from .indexacion import indice_cie10
from .negacion import analizar_negacion_en_texto
from .preprocesamiento import preprocesar_nota_clinica

# Definición de las etapas del pipeline clínico
ETAPAS_CLINICAS = [
    ("preprocesamiento", "Preprocesamiento Clínico", "Fase 2 de 6 · Ingeniería de datos", "Normalización Unicode y expansión canónica de abreviaturas médicas (HTA, DM2, dolor abd, ITU)"),
    ("recuperacion_rag", "Recuperación de Candidatos CIE-10", "Fase 3 de 6 · Ingeniería del modelo", "Búsqueda léxica BM25 sobre el catálogo oficial CIE-10 para acotar el espacio de búsqueda"),
    ("analisis_negacion", "Detección de Negación y Descarte", "Fase 3 de 6 · Ingeniería del modelo", "Algoritmo clínico NegEx en español para identificar patologías descartadas o negadas"),
    ("modelado_llm", "Asignación y Razonamiento con LLM", "Fase 3 de 6 · Ingeniería del modelo", "Inferencia estructurada (JSON Schema) para mapear hallazgos a códigos CIE-10 con evidencia textual"),
    ("auditoria_calidad", "Auditoría de Calidad y Verificación", "Fase 4 de 6 · Aseguramiento de calidad", "Verificación cruzada de códigos oficiales y comprobación de evidencia textual en la nota original"),
    ("metricas_monitoreo", "Métricas y Monitoreo", "Fase 6 de 6 · Monitoreo y mantenimiento", "Cálculo de tiempos de respuesta, tasa de codificación y distribución de estados diagnósticos"),
]

SISTEMA_CODIFICADOR = (
    "Eres un médico auditor y codificador clínico experto en la Clasificación Internacional de "
    "Enfermedades (CIE-10) del Ministerio de Salud Pública (MSP) y del IESS en Ecuador.\n"
    "Tu tarea es leer una nota de evolución médica y asignar con máxima precisión los códigos CIE-10 "
    "correspondientes a cada patología o síntoma identificado.\n"
    "Reglas estrictas:\n"
    "1. Para cada diagnóstico, indica el 'codigo_cie10', la 'descripcion_cie10' oficial, el 'termino_detectado', "
    "el 'estado' ('confirmado' o 'descartado_o_negado'), y la 'evidencia_textual' exacta (la frase de la nota que lo sustenta).\n"
    "2. Es CRÍTICO distinguir diagnósticos confirmados de aquellos que el paciente niega o que fueron descartados "
    "(ej. 'niega fiebre', 'se descarta neumonía'). Si un hallazgo está negado o descartado, márcalo obligatoriamente "
    "como 'descartado_o_negado'.\n"
    "3. No inventes códigos ni diagnósticos que no estén respaldados por el texto."
)

SCHEMA_CODIFICACION = {
    "type": "object",
    "properties": {
        "diagnosticos": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "codigo_cie10": {"type": "string", "description": "Código oficial CIE-10 (ej. I10, E11.9, J18.9)"},
                    "descripcion_cie10": {"type": "string", "description": "Descripción oficial del código"},
                    "termino_detectado": {"type": "string", "description": "Término o síntoma tal como se mencionó"},
                    "estado": {
                        "type": "string",
                        "enum": ["confirmado", "descartado_o_negado", "sospecha"],
                        "description": "Estado clínico del diagnóstico",
                    },
                    "evidencia_textual": {"type": "string", "description": "Cita textual exacta que justifica el código"},
                    "confianza": {"type": "number", "description": "Nivel de certeza de 0.0 a 1.0"},
                },
                "required": ["codigo_cie10", "descripcion_cie10", "termino_detectado", "estado", "evidencia_textual"],
            },
        },
        "resumen_caso": {"type": "string", "description": "Síntesis clínica del caso en 1-2 oraciones"},
    },
    "required": ["diagnosticos", "resumen_caso"],
}


def etapas_iniciales() -> list[dict]:
    return [
        {"clave": c, "nombre": n, "fase": f, "descripcion": d, "estado": "pendiente", "duracion_s": None, "metricas": {}}
        for c, n, f, d in ETAPAS_CLINICAS
    ]


class AnalizadorClinico:
    def __init__(self, nota: str, proveedor: str = "ollama", al_avanzar: Callable[[list[dict]], None] | None = None) -> None:
        self.nota = nota
        self.proveedor_nombre = proveedor
        self.llm: ProveedorLLM = obtener_proveedor(proveedor)
        self.al_avanzar = al_avanzar
        self.etapas = etapas_iniciales()
        self.resultado: dict = {
            "proveedor": self.llm.nombre,
            "modelo": self.llm.modelo,
            "diagnosticos": [],
            "resumen_caso": "",
        }

    def _etapa(self, clave: str) -> dict:
        return next(e for e in self.etapas if e["clave"] == clave)

    def _notificar(self) -> None:
        if self.al_avanzar:
            self.al_avanzar(self.etapas)

    def _ejecutar_paso(self, clave: str, funcion: Callable[[], None]) -> None:
        etapa = self._etapa(clave)
        etapa["estado"] = "en_curso"
        self._notificar()
        inicio = time.perf_counter()
        try:
            funcion()
            etapa["estado"] = "ok"
        except ErrorConexionLLM:
            etapa["estado"] = "error"
            raise
        except Exception as e:
            etapa["estado"] = "error"
            etapa["metricas"]["error"] = str(e)[:300]
        finally:
            etapa["duracion_s"] = round(time.perf_counter() - inicio, 2)
            self._notificar()

    def ejecutar(self) -> dict:
        inicio_total = time.perf_counter()

        # 1. Preprocesamiento Clínico
        def paso_preprocesamiento():
            self.prep = preprocesar_nota_clinica(self.nota)
            etapa = self._etapa("preprocesamiento")
            etapa["metricas"] = {
                "caracteres": self.prep["total_caracteres"],
                "palabras": self.prep["total_palabras"],
                "abreviaturas_expandidas": len(self.prep["expansiones_realizadas"]),
                "oraciones": len(self.prep["oraciones"]),
            }

        # 2. Recuperación RAG sobre Catálogo CIE-10
        def paso_recuperacion():
            texto_busqueda = f"{self.nota} {self.prep['texto_expandido']}"
            self.candidatos = indice_cie10.buscar_candidatos(texto_busqueda, top_k=10)
            etapa = self._etapa("recuperacion_rag")
            etapa["metricas"] = {
                "candidatos_recuperados": len(self.candidatos),
                "codigos_sugeridos": [c["codigo"] for c in self.candidatos],
            }

        # 3. Detección de Negaciones (NegEx)
        def paso_negaciones():
            self.hallazgos_negacion = []
            for cand in self.candidatos:
                # Comprobar si el término o sus sinónimos están negados en el texto
                for sin in [cand["descripcion"]] + cand["sinonimos"]:
                    if sin.lower() in self.nota.lower():
                        res = analizar_negacion_en_texto(self.nota, sin)
                        self.hallazgos_negacion.append({
                            "codigo": cand["codigo"],
                            "termino": sin,
                            "analisis": res,
                        })
                        break
            etapa = self._etapa("analisis_negacion")
            negados_count = sum(1 for h in self.hallazgos_negacion if h["analisis"]["estado"] == "descartado_o_negado")
            etapa["metricas"] = {
                "terminos_evaluados": len(self.hallazgos_negacion),
                "descartes_detectados": negados_count,
            }

        # 4. Asignación con LLM
        def paso_llm():
            candidatos_str = "\n".join(
                f"- Código {c['codigo']}: {c['descripcion']} (Sinónimos: {', '.join(c['sinonimos'][:3])})"
                for c in self.candidatos
            )
            prompt = (
                f"NOTA CLÍNICA ORIGINAL:\n\"\"\"{self.nota}\"\"\"\n\n"
                f"NOTA CON ABREVIATURAS EXPANDIDAS:\n\"\"\"{self.prep['texto_expandido']}\"\"\"\n\n"
                f"CATÁLOGO DE CÓDIGOS CIE-10 CANDIDATOS (RAG):\n{candidatos_str}\n\n"
                f"TAREA: Analiza la nota, extrae todos los diagnósticos y síntomas, y devuelve el objeto JSON "
                f"con los códigos CIE-10 correspondientes y su estado (confirmado vs descartado_o_negado)."
            )
            try:
                crudo = self.llm.generar_json(SISTEMA_CODIFICADOR, prompt, SCHEMA_CODIFICACION, "codificacion_cie10")
                limpio = completar_con_schema(crudo, SCHEMA_CODIFICACION)
                self.resultado["diagnosticos"] = limpio.get("diagnosticos", [])
                self.resultado["resumen_caso"] = limpio.get("resumen_caso", "")
                modelo_usado = self.llm.modelo
            except Exception as e_llm:
                # Motor Clínico de Respaldo (RAG + NegEx determinista)
                dx_fallback = []
                texto_analizar = f"{self.nota} {self.prep['texto_expandido']}"
                texto_min = texto_analizar.lower()
                codigos_vistos = set()

                for cand in self.candidatos:
                    terminos_posibles = [cand["descripcion"]] + cand["sinonimos"]
                    for t in terminos_posibles:
                        t_min = t.lower()
                        if len(t_min) >= 3 and t_min in texto_min:
                            if cand["codigo"] not in codigos_vistos:
                                codigos_vistos.add(cand["codigo"])
                                analisis_neg = analizar_negacion_en_texto(self.nota, t)
                                if analisis_neg["estado"] == "no_encontrado":
                                    analisis_neg = analizar_negacion_en_texto(self.prep["texto_expandido"], t)

                                st = "descartado_o_negado" if analisis_neg["estado"] == "descartado_o_negado" else "confirmado"
                                ev = analisis_neg.get("evidencia") or f"Mención de {t} en la nota clínica"

                                dx_fallback.append({
                                    "codigo_cie10": cand["codigo"],
                                    "descripcion_cie10": cand["descripcion"],
                                    "termino_detectado": t,
                                    "estado": st,
                                    "evidencia_textual": ev,
                                    "confianza": 0.95,
                                    "motivo_descarte": analisis_neg.get("justificacion") if st == "descartado_o_negado" else None,
                                })
                            break

                self.resultado["diagnosticos"] = dx_fallback
                motivo = "Falta ANTHROPIC_API_KEY en .env" if self.proveedor_nombre == "claude" else f"Fallo LLM: {str(e_llm)[:80]}"
                self.resultado["resumen_caso"] = f"Análisis procesado mediante Motor Clínico Determinista (RAG + NegEx) [{motivo}]."
                modelo_usado = f"{self.llm.modelo} (Respaldo RAG+NegEx)"
                self.resultado["modelo"] = modelo_usado

            etapa = self._etapa("modelado_llm")
            etapa["metricas"] = {
                "diagnosticos_generados": len(self.resultado["diagnosticos"]),
                "modelo_usado": modelo_usado,
            }

        # 5. Auditoría de Calidad Determinista (Post-procesamiento)
        def paso_auditoria():
            diagnosticos_validados = []
            for dx in self.resultado["diagnosticos"]:
                cod = dx.get("codigo_cie10", "").strip().upper()
                info_cat = buscar_en_catalogo(cod)

                # Validar existencia oficial en catálogo
                if info_cat:
                    dx["descripcion_oficial"] = info_cat["descripcion"]
                    dx["capitulo"] = info_cat["capitulo"]
                else:
                    dx["descripcion_oficial"] = dx.get("descripcion_cie10", "No tipificado")
                    dx["capitulo"] = "Otros códigos"

                # Comprobación de evidencia textual en nota original
                evidencia = dx.get("evidencia_textual", "")
                dx["evidencia_verificada"] = bool(evidencia and (evidencia.lower() in self.nota.lower() or evidencia.lower() in self.prep["texto_expandido"].lower()))

                # Reconciliación con regla NegEx determinista
                analisis_neg = analizar_negacion_en_texto(self.nota, dx.get("termino_detectado", ""))
                if analisis_neg["estado"] == "descartado_o_negado":
                    dx["estado"] = "descartado_o_negado"
                    dx["motivo_descarte"] = analisis_neg["justificacion"]

                diagnosticos_validados.append(dx)

            self.resultado["diagnosticos"] = diagnosticos_validados
            etapa = self._etapa("auditoria_calidad")
            etapa["metricas"] = {
                "codigos_validados": len(diagnosticos_validados),
                "evidencias_verificadas": sum(1 for d in diagnosticos_validados if d.get("evidencia_verificada")),
                "confirmados": sum(1 for d in diagnosticos_validados if d.get("estado") == "confirmado"),
                "descartados": sum(1 for d in diagnosticos_validados if d.get("estado") == "descartado_o_negado"),
            }

        # 6. Métricas de Monitoreo
        def paso_monitoreo():
            duracion = round(time.perf_counter() - inicio_total, 2)
            etapa = self._etapa("metricas_monitoreo")
            etapa["metricas"] = {
                "duracion_total_s": duracion,
                "proveedor": self.llm.nombre,
                "modelo": self.llm.modelo,
                "total_diagnosticos": len(self.resultado["diagnosticos"]),
            }
            self.resultado["duracion_s"] = duracion

        pasos = [
            ("preprocesamiento", paso_preprocesamiento),
            ("recuperacion_rag", paso_recuperacion),
            ("analisis_negacion", paso_negaciones),
            ("modelado_llm", paso_llm),
            ("auditoria_calidad", paso_auditoria),
            ("metricas_monitoreo", paso_monitoreo),
        ]

        for clave, func in pasos:
            self._ejecutar_paso(clave, func)

        return self.resultado

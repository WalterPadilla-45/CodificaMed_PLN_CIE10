"""Interfaz común para proveedores de LLM en CodificaMed."""
from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from typing import Any


class ErrorLLM(Exception):
    """Fallo en la comunicación con el modelo o interpretación de respuesta."""


class ErrorConexionLLM(ErrorLLM):
    """Proveedor inaccesible o apagado."""


class ProveedorLLM(ABC):
    nombre: str = "base"
    modelo: str = ""

    @abstractmethod
    def generar_json(self, sistema: str, prompt: str, schema: dict, nombre: str) -> dict:
        """Devuelve un objeto dict validado contra el esquema JSON indicado."""

    @abstractmethod
    def estado(self) -> dict:
        """Estado de salud y disponibilidad del modelo."""


def extraer_json(texto: str) -> dict:
    """Extrae un JSON válido incluso si el modelo incluye bloques markdown."""
    texto = texto.strip()
    texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto)
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        inicio, fin = texto.find("{"), texto.rfind("}")
        if inicio != -1 and fin > inicio:
            try:
                return json.loads(texto[inicio : fin + 1])
            except json.JSONDecodeError:
                pass
    raise ErrorLLM("La respuesta del modelo no contiene una estructura JSON válida.")


def completar_con_schema(dato: Any, schema: dict) -> Any:
    """Rellena con valores por defecto cualquier campo omitido por el modelo."""
    tipo = schema.get("type")
    if tipo == "object":
        dato = dato if isinstance(dato, dict) else {}
        for clave, sub in schema.get("properties", {}).items():
            dato[clave] = completar_con_schema(dato.get(clave), sub)
        return dato
    if tipo == "array":
        if not isinstance(dato, list):
            return []
        return [completar_con_schema(x, schema.get("items", {})) for x in dato]
    if tipo == "string":
        if dato is None:
            return ""
        if "enum" in schema and str(dato) not in schema["enum"]:
            return schema["enum"][0]
        return str(dato)
    if tipo in ("number", "integer"):
        try:
            return float(dato) if tipo == "number" else int(float(dato))
        except (TypeError, ValueError):
            return 0
    if tipo == "boolean":
        if isinstance(dato, bool):
            return dato
        return str(dato).strip().lower() in {"true", "si", "sí", "1", "yes"}
    return dato

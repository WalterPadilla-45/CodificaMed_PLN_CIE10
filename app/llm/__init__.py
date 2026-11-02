"""Fábrica de proveedores de LLM para CodificaMed."""
from __future__ import annotations

from ..config import settings
from .base import ErrorConexionLLM, ErrorLLM, ProveedorLLM
from .claude import ProveedorClaude
from .ollama import ProveedorOllama
from .simulado import ProveedorSimulado

PROVEEDORES = {
    "ollama": ProveedorOllama,
    "claude": ProveedorClaude,
    "simulado": ProveedorSimulado,
}


def obtener_proveedor(nombre: str | None = None) -> ProveedorLLM:
    nombre = (nombre or settings.llm_provider).lower()
    if nombre not in PROVEEDORES:
        raise ErrorLLM(f"Proveedor desconocido: '{nombre}'. Válidos: {list(PROVEEDORES.keys())}")
    return PROVEEDORES[nombre]()


__all__ = ["ErrorConexionLLM", "ErrorLLM", "ProveedorLLM", "obtener_proveedor", "PROVEEDORES"]

"""Proveedor local con Ollama (soporta llama3.2, mistral, qwen2.5, etc.)."""
from __future__ import annotations

import json
import httpx

from ..config import settings
from .base import ErrorConexionLLM, ErrorLLM, ProveedorLLM, extraer_json


class ProveedorOllama(ProveedorLLM):
    nombre = "ollama"

    def __init__(self) -> None:
        self.host = settings.ollama_host
        self.modelo = settings.ollama_model

    def _chat(self, sistema: str, prompt: str, schema: dict | None) -> str:
        cuerpo = {
            "model": self.modelo,
            "messages": [
                {"role": "system", "content": sistema},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.05,  # Muy baja temperatura para asignación clínica precisa
                "num_ctx": settings.ollama_num_ctx,
            },
        }
        if schema is not None:
            cuerpo["format"] = "json"
        try:
            r = httpx.post(f"{self.host}/api/chat", json=cuerpo, timeout=settings.ollama_timeout)
        except httpx.ConnectError as e:
            raise ErrorConexionLLM(f"No se pudo conectar a Ollama en {self.host}. ¿Está iniciado?") from e
        except httpx.TimeoutException as e:
            raise ErrorLLM("Ollama agotó el tiempo de espera (timeout).") from e

        if r.status_code == 404:
            raise ErrorConexionLLM(f"El modelo '{self.modelo}' no está descargado en Ollama.")
        if r.status_code >= 400:
            raise ErrorLLM(f"Ollama respondió error {r.status_code}: {r.text[:300]}")

        return r.json().get("message", {}).get("content", "")

    def generar_json(self, sistema: str, prompt: str, schema: dict, nombre: str) -> dict:
        sistema_json = (
            f"{sistema}\n\nIMPORTANTE: Responde ÚNICAMENTE con un objeto JSON válido que cumpla este esquema:\n"
            f"{json.dumps(schema, ensure_ascii=False)}"
        )
        for intento in range(2):
            try:
                resp = self._chat(sistema_json, prompt, schema)
                return extraer_json(resp)
            except ErrorConexionLLM:
                raise
            except ErrorLLM:
                if intento == 1:
                    raise
        raise ErrorLLM("Fallo al obtener JSON válido de Ollama.")

    def estado(self) -> dict:
        try:
            r = httpx.get(f"{self.host}/api/tags", timeout=3)
            instalados = [m["name"] for m in r.json().get("models", [])]
        except Exception:
            return {
                "disponible": False,
                "modelo": self.modelo,
                "mensaje": "Ollama no responde en 127.0.0.1:11434",
                "instalados": [],
            }

        def presente(nombre: str) -> bool:
            base = nombre if ":" in nombre else f"{nombre}:latest"
            return any(m == nombre or m == base for m in instalados)

        modelo_ok = presente(self.modelo)
        return {
            "disponible": modelo_ok,
            "modelo": self.modelo,
            "mensaje": "Listo (Ollama activo)" if modelo_ok else f"Descarga pendiente: ollama pull {self.modelo}",
            "instalados": instalados,
        }

"""Proveedor en la nube: Claude (Anthropic API) con Tool Use forzado."""
from __future__ import annotations

from ..config import settings
from .base import ErrorConexionLLM, ErrorLLM, ProveedorLLM, extraer_json


class ProveedorClaude(ProveedorLLM):
    nombre = "claude"

    def __init__(self) -> None:
        self.modelo = settings.claude_model
        self._cliente = None

    def _cliente_api(self):
        if not settings.anthropic_api_key:
            raise ErrorConexionLLM("Falta ANTHROPIC_API_KEY en el archivo .env")
        if self._cliente is None:
            import anthropic
            self._cliente = anthropic.Anthropic(api_key=settings.anthropic_api_key, max_retries=2)
        return self._cliente

    def generar_json(self, sistema: str, prompt: str, schema: dict, nombre: str) -> dict:
        import anthropic
        try:
            respuesta = self._cliente_api().messages.create(
                model=self.modelo,
                max_tokens=4000,
                system=sistema,
                messages=[{"role": "user", "content": prompt}],
                tools=[
                    {
                        "name": nombre,
                        "description": "Genera los diagnósticos codificados con CIE-10 y evidencia.",
                        "input_schema": schema,
                    }
                ],
                tool_choice={"type": "tool", "name": nombre},
            )
        except anthropic.AuthenticationError as e:
            raise ErrorConexionLLM("La clave ANTHROPIC_API_KEY no es válida.") from e
        except anthropic.APIConnectionError as e:
            raise ErrorConexionLLM("Error de conexión con los servidores de Anthropic.") from e
        except anthropic.APIError as e:
            raise ErrorLLM(f"Error devuelto por la API de Claude: {e}") from e

        for bloque in respuesta.content:
            if bloque.type == "tool_use":
                return dict(bloque.input)

        texto = "".join(b.text for b in respuesta.content if b.type == "text")
        return extraer_json(texto)

    def estado(self) -> dict:
        configurado = bool(settings.anthropic_api_key)
        return {
            "disponible": configurado,
            "modelo": self.modelo,
            "mensaje": "API key configurada" if configurado else "Falta configurar ANTHROPIC_API_KEY en .env",
            "instalados": [self.modelo] if configurado else [],
        }

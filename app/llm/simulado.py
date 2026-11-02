"""Proveedor simulado para pruebas unitarias sin GPU ni API keys."""
from __future__ import annotations

from .base import ProveedorLLM


class ProveedorSimulado(ProveedorLLM):
    nombre = "simulado"
    modelo = "simulado-v1"

    def generar_json(self, sistema: str, prompt: str, schema: dict, nombre: str) -> dict:
        # Devuelve diagnósticos sintéticos coherentes
        return {
            "diagnosticos": [
                {
                    "codigo_cie10": "I10",
                    "descripcion_cie10": "Hipertensión esencial (primaria)",
                    "termino_detectado": "HTA",
                    "estado": "confirmado",
                    "evidencia_textual": "paciente con antecedente de HTA",
                    "confianza": 0.95,
                },
                {
                    "codigo_cie10": "J18.9",
                    "descripcion_cie10": "Neumonía, no especificada",
                    "termino_detectado": "neumonía",
                    "estado": "descartado_o_negado",
                    "evidencia_textual": "se descarta neumonía en radiografía de tórax",
                    "confianza": 0.92,
                },
            ],
            "resumen_caso": "Paciente hipertenso con cuadro respiratorio donde se descartó neumonía.",
        }

    def estado(self) -> dict:
        return {"disponible": True, "modelo": "simulado-v1", "mensaje": "Modo de simulación (tests rápidos)", "instalados": ["simulado-v1"]}

"""Pipeline de Procesamiento de Lenguaje Natural para CodificaMed."""
from .orquestador import AnalizadorClinico, ETAPAS_CLINICAS
from .catalogo import CATALOGO_CIE10
from .preprocesamiento import preprocesar_nota_clinica
from .negacion import analizar_negacion_en_texto
from .evaluacion import CASOS_EVALUACION, calcular_metricas, benchmark_modelos_referencia

__all__ = [
    "AnalizadorClinico",
    "ETAPAS_CLINICAS",
    "CATALOGO_CIE10",
    "preprocesar_nota_clinica",
    "analizar_negacion_en_texto",
    "CASOS_EVALUACION",
    "calcular_metricas",
    "benchmark_modelos_referencia",
]

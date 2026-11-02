"""FASE 2 CRISP-ML(Q) — Preprocesamiento del texto clínico.

Incluye:
1. Normalización Unicode (NFC, eliminación de caracteres de control).
2. Expansión canónica de abreviaturas médicas (HTA, DM2, dolor abd, ITU, IAM, etc.).
3. Segmentación en oraciones preservando referencias anatómicas y signos vitales.
"""
from __future__ import annotations

import re
import unicodedata

# Diccionario especializado de abreviaturas clínicas en español
ABREVIATURAS_CLINICAS = [
    (r"\bhta\b", "hipertensión arterial"),
    (r"\bdm2\b", "diabetes mellitus tipo 2"),
    (r"\bdmnid\b", "diabetes mellitus tipo 2 no insulinodependiente"),
    (r"\bdm1\b", "diabetes mellitus tipo 1"),
    (r"\bdmid\b", "diabetes mellitus tipo 1 insulinodependiente"),
    (r"\bdolor\s+abd\b", "dolor abdominal"),
    (r"\bitu\b", "infección del tracto urinario"),
    (r"\bivu\b", "infección de vías urinarias"),
    (r"\biam\b", "infarto agudo de miocardio"),
    (r"\bepoc\b", "enfermedad pulmonar obstructiva crónica"),
    (r"\bacv\b", "accidente cerebrovascular"),
    (r"\bevc\b", "evento vascular cerebral"),
    (r"\bira\b", "infección respiratoria aguda"),
    (r"\beda\b", "enfermedad diarreica aguda"),
    (r"\berge\b", "enfermedad por reflujo gastroesofágico"),
    (r"\berc\b", "enfermedad renal crónica"),
    (r"\birc\b", "insuficiencia renal crónica"),
    (r"\bicc\b", "insuficiencia cardíaca congestiva"),
    (r"\brx\b", "radiografía"),
    (r"\btac\b", "tomografía computarizada"),
    (r"\becg\b|\bekg\b", "electrocardiograma"),
    (r"\bfid\b", "fosa ilíaca derecha"),
    (r"\bfii\b", "fosa ilíaca izquierda"),
    (r"\bmeg\b", "mal estado general"),
    (r"\bbeg\b", "buen estado general"),
    (r"\bap\b", "antecedentes personales"),
    (r"\bapp\b", "antecedentes personales patológicos"),
    (r"\bapf\b", "antecedentes patológicos familiares"),
]


def normalizar_texto(texto: str) -> str:
    """Limpia caracteres extraños manteniendo acentos y puntuación clínica."""
    texto = unicodedata.normalize("NFC", texto)
    # Reemplazo de saltos múltiples y tabuladores
    texto = re.sub(r"[\r\t]+", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def expandir_abreviaturas(texto: str) -> tuple[str, list[dict]]:
    """Expande siglas médicas conservando la trazabilidad de los cambios."""
    texto_expandido = texto
    expansiones = []

    for patron, reemplazo in ABREVIATURAS_CLINICAS:
        for match in re.finditer(patron, texto_expandido, flags=re.IGNORECASE):
            original = match.group(0)
            expansiones.append({"original": original, "expandido": reemplazo, "posicion": match.start()})
        texto_expandido = re.sub(patron, reemplazo, texto_expandido, flags=re.IGNORECASE)

    return texto_expandido, expansiones


def segmentar_oraciones(texto: str) -> list[str]:
    """Segmenta la nota clínica en unidades de sentido (oraciones/cláusulas)."""
    # Corta por punto, punto y coma o saltos lógicos, evitando cortar abreviaturas numéricas
    partes = re.split(r"(?<=[.;:\n])\s+", texto)
    oraciones = [p.strip() for p in partes if len(p.strip()) > 3]
    return oraciones if oraciones else [texto]


def preprocesar_nota_clinica(nota: str) -> dict:
    """Ejecuta el pipeline completo de preprocesamiento clínico."""
    limpio = normalizar_texto(nota)
    expandido, expansiones = expandir_abreviaturas(limpio)
    oraciones = segmentar_oraciones(limpio)

    return {
        "texto_normalizado": limpio,
        "texto_expandido": expandido,
        "total_caracteres": len(limpio),
        "total_palabras": len(limpio.split()),
        "expansiones_realizadas": expansiones,
        "oraciones": oraciones,
    }

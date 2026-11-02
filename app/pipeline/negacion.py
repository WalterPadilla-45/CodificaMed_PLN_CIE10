"""Módulo especializado de Detección de Negación y Descarte Clínico (NegEx en Español).

Distingue diagnósticos confirmados de aquellos explícitamente negados por el paciente
o descartados en estudios paraclínicos (e.g. "niega fiebre", "se descarta neumonía").
"""
from __future__ import annotations

import re

# Disparadores que preceden a un término clínico negado (Pre-Negación)
GATILLOS_PRE_NEGACION = [
    r"\bniega\b",
    r"\bnego\b",
    r"\bnegó\b",
    r"\bsin\s+evidencia\s+de\b",
    r"\bsin\s+signos\s+de\b",
    r"\bsin\s+hallazgos\s+de\b",
    r"\bsin\s+datos\s+de\b",
    r"\bsin\b",
    r"\bno\s+presenta\b",
    r"\bno\s+refiere\b",
    r"\bno\s+se\s+evidencia\b",
    r"\bno\s+se\s+observa\b",
    r"\bno\s+se\s+palpa\b",
    r"\bno\s+impresiona\b",
    r"\bno\s+hay\b",
    r"\bse\s+descarta\b",
    r"\bdescartado\b",
    r"\bdescartada\b",
    r"\bdescartando\b",
    r"\bdescarta\b",
    r"\bausencia\s+de\b",
    r"\bnegativo\s+para\b",
    r"\basintomatico\s+para\b",
    r"\basintomático\s+para\b",
    r"\blibre\s+de\b",
]

# Disparadores posteriores al término clínico (Post-Negación)
GATILLOS_POST_NEGACION = [
    r"\bfue\s+descartado\b",
    r"\bfue\s+descartada\b",
    r"\bqueda\s+descartado\b",
    r"\bqueda\s+descartada\b",
    r"\bes\s+negativo\b",
    r"\bes\s+negativa\b",
    r"\bresulto\s+negativo\b",
    r"\bresultó\s+negativo\b",
    r"\bnegativo\b",
]

# Expresiones que contienen 'no' o 'sin' pero NO constituyen negación patológica (Pseudo-Negaciones)
PSEUDO_NEGACIONES = [
    r"\bsin\s+cambios\b",
    r"\bsin\s+duda\b",
    r"\bsin\s+embargo\b",
    r"\bno\s+solo\b",
    r"\bno\s+obstante\b",
    r"\bno\s+es\s+posible\s+descartar\b",
]

# Delimitadores de ámbito (Scope boundaries) que detienen la propagación de la negación
TERMINADORES_AMBITO = [
    r"[,;.:]",
    r"\bpero\b",
    r"\bsin\s+embargo\b",
    r"\baunque\b",
    r"\bcon\b",
    r"\bpresentando\b",
    r"\brefiriendo\b",
    r"\bse\s+confirma\b",
    r"\by\s+se\s+evidencia\b",
    r"\bademas\b",
    r"\bademás\b",
    r"\bno\s+obstante\b",
]


def analizar_negacion_en_texto(texto: str, termino: str) -> dict:
    """Evalúa si un término clínico específico está negado, descartado o confirmado dentro del texto."""
    texto_min = texto.lower()
    termino_min = termino.lower()

    pos_termino = texto_min.find(termino_min)
    if pos_termino == -1:
        return {
            "estado": "no_encontrado",
            "justificacion": f"El término '{termino}' no se localizó en la nota.",
            "gatillo": None,
            "evidencia": "",
        }

    # Ventana de contexto alrededor del término (80 caracteres antes y después)
    inicio_ventana = max(0, pos_termino - 80)
    fin_ventana = min(len(texto), pos_termino + len(termino) + 80)
    fragmento = texto[inicio_ventana:fin_ventana]
    fragmento_min = fragmento.lower()

    # Comprobar pseudo-negaciones
    for pseudo in PSEUDO_NEGACIONES:
        if re.search(pseudo, fragmento_min):
            return {
                "estado": "confirmado",
                "justificacion": "Aparece en contexto afirmativo (pseudo-negación descartada).",
                "gatillo": None,
                "evidencia": fragmento.strip(),
            }

    # Evaluar Pre-Negaciones (a la izquierda del término)
    segmento_previo = texto_min[inicio_ventana:pos_termino]
    # Cortar por terminadores de ámbito a la izquierda
    for lim in TERMINADORES_AMBITO:
        coincidencias = list(re.finditer(lim, segmento_previo))
        if coincidencias:
            ultimo_corte = coincidencias[-1].end()
            segmento_previo = segmento_previo[ultimo_corte:]

    for gatillo in GATILLOS_PRE_NEGACION:
        m = re.search(gatillo, segmento_previo)
        if m:
            gatillo_str = m.group(0)
            evidencia = texto[inicio_ventana + m.start() : min(len(texto), pos_termino + len(termino) + 25)]
            return {
                "estado": "descartado_o_negado",
                "justificacion": f"Antecedido por gatillo de negación/descarte: '{gatillo_str}'.",
                "gatillo": gatillo_str,
                "evidencia": evidencia.strip(),
            }

    # Evaluar Post-Negaciones (a la derecha del término)
    segmento_posterior = texto_min[pos_termino + len(termino_min) : fin_ventana]
    for lim in TERMINADORES_AMBITO:
        m_corte = re.search(lim, segmento_posterior)
        if m_corte:
            segmento_posterior = segmento_posterior[: m_corte.start()]

    for gatillo in GATILLOS_POST_NEGACION:
        m = re.search(gatillo, segmento_posterior)
        if m:
            gatillo_str = m.group(0)
            evidencia = texto[max(0, pos_termino - 20) : pos_termino + len(termino) + m.end()]
            return {
                "estado": "descartado_o_negado",
                "justificacion": f"Seguido por gatillo de descarte: '{gatillo_str}'.",
                "gatillo": gatillo_str,
                "evidencia": evidencia.strip(),
            }

    # Si no hay gatillos de negación, se considera confirmado / afirmativo
    evidencia_confirmada = texto[max(0, pos_termino - 25) : min(len(texto), pos_termino + len(termino) + 30)]
    return {
        "estado": "confirmado",
        "justificacion": "No se detectaron estructuras gramaticales de negación o descarte.",
        "gatillo": None,
        "evidencia": evidencia_confirmada.strip(),
    }

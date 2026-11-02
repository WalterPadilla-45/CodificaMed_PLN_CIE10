"""FASE 2 / 3 CRISP-ML(Q) — Indexación y Recuperación Léxica BM25 sobre el Catálogo CIE-10.

Permite recuperar los códigos diagnósticos candidatos más relevantes para una nota clínica,
sirviendo como la capa de Recuperación (R) para el pipeline RAG.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter

from .catalogo import CATALOGO_CIE10

try:
    import snowballstemmer
    _stemmer = snowballstemmer.stemmer("spanish")
except ImportError:
    _stemmer = None

STOPWORDS_MEDICAS = set(
    """a al algo algunos ante antes como con contra de del desde donde durante e el ella ellas ellos en entre
    era es esa esas ese eso esos esta estas este esto estos fue ha han hasta hay la las le les lo los mas me
    mi mismo muy ni no nos o otra otras otro otros para pero poco por porque que quien se sea segun ser si sin
    sino sobre su sus tal tambien tanto te tiene todo todos tu un una uno unos y ya paciente refiere presenta
    acude refiere antecedentes cuadro valoracion""".split()
)


def _sin_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def tokenizar(texto: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9ñ]+", _sin_tildes(texto.lower()))
    tokens = [t for t in tokens if t not in STOPWORDS_MEDICAS and len(t) > 1]
    if _stemmer:
        tokens = _stemmer.stemWords(tokens)
    return tokens


class IndiceCIE10:
    def __init__(self, catalogo: list[dict] = CATALOGO_CIE10) -> None:
        self.catalogo = catalogo
        self._construir_bm25()

    def _construir_bm25(self, k1: float = 1.4, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.documentos = []
        for item in self.catalogo:
            corpus_item = f"{item['codigo']} {item['descripcion']} {' '.join(item['sinonimos'])}"
            self.documentos.append(Counter(tokenizar(corpus_item)))

        self.longitudes = [sum(doc.values()) for doc in self.documentos]
        self.long_media = (sum(self.longitudes) / len(self.longitudes)) if self.longitudes else 1

        df: Counter[str] = Counter()
        for doc in self.documentos:
            df.update(doc.keys())

        n = len(self.documentos)
        self.idf = {term: math.log(1 + (n - freq + 0.5) / (freq + 0.5)) for term, freq in df.items()}
        self.vocabulario = len(df)

    def buscar_candidatos(self, consulta: str, top_k: int = 8) -> list[dict]:
        """Calcula el puntaje BM25 de cada código del catálogo contra la consulta clínica."""
        tokens_q = tokenizar(consulta)
        if not tokens_q:
            return self.catalogo[:top_k]

        puntajes = []
        for i, (doc, largo) in enumerate(zip(self.documentos, self.longitudes)):
            score = 0.0
            for t in tokens_q:
                if t in doc:
                    tf = doc[t]
                    score += self.idf.get(t, 0.0) * tf * (self.k1 + 1) / (
                        tf + self.k1 * (1 - self.b + self.b * largo / self.long_media)
                    )
            if score > 0:
                puntajes.append((i, score))

        puntajes.sort(key=lambda x: x[1], reverse=True)
        seleccionados = [self.catalogo[idx] for idx, _ in puntajes[:top_k]]

        # Si hay pocos candidatos recuperados, complementar con los primeros del catálogo
        if len(seleccionados) < 3:
            for c in self.catalogo:
                if c not in seleccionados:
                    seleccionados.append(c)
                if len(seleccionados) >= top_k:
                    break

        return seleccionados


# Instancia singleton precalculada
indice_cie10 = IndiceCIE10()

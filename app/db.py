"""Persistencia con SQLite para el historial de codificaciones clínicas."""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime

from .config import settings

_lock = threading.Lock()
_conn = sqlite3.connect(settings.db_path, check_same_thread=False)
_conn.row_factory = sqlite3.Row

_conn.executescript(
    """
    CREATE TABLE IF NOT EXISTS codificaciones (
        id TEXT PRIMARY KEY,
        titulo TEXT NOT NULL,
        nota_original TEXT NOT NULL,
        proveedor TEXT NOT NULL,
        modelo TEXT NOT NULL,
        diagnosticos TEXT NOT NULL,
        etapas TEXT NOT NULL,
        metricas TEXT,
        creado TEXT NOT NULL,
        duracion_s REAL
    );
    """
)
_conn.commit()


def ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _ejecutar(sql: str, params: tuple = ()) -> sqlite3.Cursor:
    with _lock:
        cur = _conn.execute(sql, params)
        _conn.commit()
        return cur


def _consultar(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with _lock:
        return _conn.execute(sql, params).fetchall()


def guardar_codificacion(
    id_: str,
    titulo: str,
    nota: str,
    proveedor: str,
    modelo: str,
    diagnosticos: list[dict],
    etapas: list[dict],
    metricas: dict,
    duracion_s: float,
) -> None:
    _ejecutar(
        """
        INSERT INTO codificaciones (id, titulo, nota_original, proveedor, modelo, diagnosticos, etapas, metricas, creado, duracion_s)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            id_,
            titulo,
            nota,
            proveedor,
            modelo,
            json.dumps(diagnosticos, ensure_ascii=False),
            json.dumps(etapas, ensure_ascii=False),
            json.dumps(metricas, ensure_ascii=False),
            ahora(),
            round(duracion_s, 2),
        ),
    )


def listar_codificaciones() -> list[dict]:
    filas = _consultar("SELECT id, titulo, proveedor, modelo, diagnosticos, creado, duracion_s FROM codificaciones ORDER BY creado DESC")
    res = []
    for f in filas:
        dx = json.loads(f["diagnosticos"]) if f["diagnosticos"] else []
        res.append({
            "id": f["id"],
            "titulo": f["titulo"],
            "proveedor": f["proveedor"],
            "modelo": f["modelo"],
            "total_diagnosticos": len(dx),
            "confirmados": sum(1 for d in dx if d.get("estado") == "confirmado"),
            "descartados": sum(1 for d in dx if d.get("estado") == "descartado_o_negado"),
            "creado": f["creado"],
            "duracion_s": f["duracion_s"],
        })
    return res


def obtener_codificacion(id_: str) -> dict | None:
    filas = _consultar("SELECT * FROM codificaciones WHERE id = ?", (id_,))
    if not filas:
        return None
    f = filas[0]
    return {
        "id": f["id"],
        "titulo": f["titulo"],
        "nota_original": f["nota_original"],
        "proveedor": f["proveedor"],
        "modelo": f["modelo"],
        "diagnosticos": json.loads(f["diagnosticos"]),
        "etapas": json.loads(f["etapas"]),
        "metricas": json.loads(f["metricas"]) if f["metricas"] else {},
        "creado": f["creado"],
        "duracion_s": f["duracion_s"],
    }

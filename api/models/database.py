import os
import aiosqlite
from contextlib import asynccontextmanager

DB_PATH = os.getenv("DB_PATH", "/data/aguacatia.db")

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS clasificaciones (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario     TEXT    NOT NULL DEFAULT 'anonimo',
    imagen_url  TEXT    NOT NULL,
    clase       TEXT    NOT NULL,
    confianza   REAL    NOT NULL,
    fecha_at    TEXT    NOT NULL
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TABLE)
        await db.commit()


@asynccontextmanager
async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def insert_clasificacion(usuario: str, imagen_url: str, clase: str, confianza: float, fecha_at: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO clasificaciones (usuario, imagen_url, clase, confianza, fecha_at) VALUES (?, ?, ?, ?, ?)",
            (usuario, imagen_url, clase, confianza, fecha_at),
        )
        await db.commit()
        return cursor.lastrowid


async def get_history(page: int, limit: int, usuario: str | None) -> tuple[int, list[dict]]:
    offset = (page - 1) * limit
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        if usuario:
            total_row = await db.execute("SELECT COUNT(*) FROM clasificaciones WHERE usuario = ?", (usuario,))
            rows = await db.execute(
                "SELECT * FROM clasificaciones WHERE usuario = ? ORDER BY id DESC LIMIT ? OFFSET ?",
                (usuario, limit, offset),
            )
        else:
            total_row = await db.execute("SELECT COUNT(*) FROM clasificaciones")
            rows = await db.execute(
                "SELECT * FROM clasificaciones ORDER BY id DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )

        total = (await total_row.fetchone())[0]
        items = [dict(row) for row in await rows.fetchall()]
        return total, items

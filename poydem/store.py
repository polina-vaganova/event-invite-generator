"""
Каталог событий в Postgres.

Имитирует базу данных Афиши. Событие хранится целиком в JSONB-колонке `data`,
поэтому структура совпадает с тем, что отдаёт парсер и ждут шаблоны —
никакого ручного маппинга полей.
"""
from psycopg.types.json import Json

from .db import get_conn


def get_all_events() -> list[dict]:
    """Все события каталога (новые — первыми по дате парсинга)."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT data FROM events ORDER BY (data->>'parsedAt') DESC"
        ).fetchall()
    return [r["data"] for r in rows]


def get_event(event_id: str) -> dict | None:
    """Одно событие по ID или None."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT data FROM events WHERE id = %s", (event_id,)
        ).fetchone()
    return row["data"] if row else None


def add_event(event: dict) -> dict:
    """Добавляет (или обновляет) событие в каталоге."""
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO events (id, data) VALUES (%s, %s) "
            "ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data",
            (event["id"], Json(event)),
        )
        conn.commit()
    return event

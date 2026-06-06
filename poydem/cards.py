"""
Сгенерированные открытки: сохранение в БД и чтение.

Текст и метаданные — в таблице `cards`. Сама картинка-открытка сохраняется
ФАЙЛОМ в static/cards/<id>.png, а в БД хранится только имя файла (image_file).
"""
import secrets

from .db import get_conn


def new_card_id() -> str:
    """Короткий случайный ID для открытки (для ссылки /card/<id>)."""
    return secrets.token_urlsafe(8)


def save_card(
    card_id: str,
    event_id: str,
    recipient: str,
    style: str,
    message: str,
    image_file: str,
) -> str:
    """Сохраняет открытку в БД и возвращает её ID."""
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO cards (id, event_id, recipient, style, message, image_file) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (card_id, event_id, recipient, style, message, image_file),
        )
        conn.commit()
    return card_id


def get_card(card_id: str) -> dict | None:
    """Открытка по ID или None."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM cards WHERE id = %s", (card_id,)).fetchone()
    return row

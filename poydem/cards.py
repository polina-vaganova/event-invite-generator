"""
Сгенерированные открытки: сохранение в БД и чтение.

Текст и метаданные — в таблице `cards`. Сама картинка сохраняется ФАЙЛОМ
в static/cards/<id>.png (это делает Pillow на этапе ИИ), а в БД хранится
только имя файла.

TODO (команда):
  • в save_card() уже сохраняется текст; добавьте генерацию картинки (Pillow)
    и передавайте image_file;
  • страницу /card/<id> (лендинг для получателя) — см. studio.py.
"""
import secrets

from .db import get_conn


def new_card_id() -> str:
    """Короткий случайный ID для открытки (для ссылки /card/<id>)."""
    return secrets.token_urlsafe(8)


def save_card(
    event_id: str,
    recipient: str,
    relationship: str,
    tone: str,
    style: str,
    bg: str,
    message: str,
    image_file: str | None = None,
) -> str:
    """Сохраняет открытку и возвращает её ID."""
    card_id = new_card_id()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO cards "
            "(id, event_id, recipient, relationship, tone, style, bg, message, image_file) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (card_id, event_id, recipient, relationship, tone, style, bg, message, image_file),
        )
        conn.commit()
    return card_id


def get_card(card_id: str) -> dict | None:
    """Открытка по ID или None."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM cards WHERE id = %s", (card_id,)).fetchone()
    return row

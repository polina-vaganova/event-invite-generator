"""
Хранилище каталога событий.

Имитирует базу данных Афиши: читает события из data/events.json и позволяет
добавлять новые (через фичу «добавить по ссылке»). Для прототипа JSON-файла
достаточно — никакой отдельной БД не нужно.
"""
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "events.json"


def _read_all() -> list[dict]:
    """Читает все события из файла (или пустой список, если файла нет)."""
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _write_all(events: list[dict]) -> None:
    DATA_FILE.write_text(
        json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def get_all_events() -> list[dict]:
    """Все события каталога."""
    return _read_all()


def get_event(event_id: str) -> dict | None:
    """Одно событие по ID или None."""
    for event in _read_all():
        if event.get("id") == event_id:
            return event
    return None


def add_event(event: dict) -> dict:
    """
    Добавляет (или обновляет) событие в каталоге. Новое встаёт в начало списка,
    чтобы сразу было видно в каталоге.
    """
    events = _read_all()
    for i, existing in enumerate(events):
        if existing.get("id") == event["id"]:
            events[i] = event
            _write_all(events)
            return event
    events.insert(0, event)
    _write_all(events)
    return event

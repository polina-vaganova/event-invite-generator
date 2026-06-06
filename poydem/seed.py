"""
Создаёт таблицы и наполняет каталог событиями из data/events.json.

Запуск: python -m poydem.seed   (или `make seed`)

Не обращается к Афише — берёт готовый снимок из файла. Идемпотентно:
повторный запуск просто обновит существующие события.
"""
import json
from pathlib import Path

from .db import init_db
from .store import add_event

DATA_FILE = Path(__file__).parent / "data" / "events.json"


def main() -> None:
    init_db()
    events = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    for event in events:
        add_event(event)
        print(f"✓ [{event.get('category')}] {event.get('title')}")
    print(f"\nЗагружено {len(events)} событий в БД")


if __name__ == "__main__":
    main()

"""
Подключение к Postgres.

Простой слой поверх psycopg: одна функция get_conn() для соединения и init_db()
для создания таблиц из schema.sql. Для прототипа соединение открывается на
операцию — этого достаточно и проще пула.
"""
import os
import time
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://poydem:poydem@localhost:5433/poydem"
)

SCHEMA_FILE = Path(__file__).parent / "schema.sql"


def get_conn() -> psycopg.Connection:
    """Открывает соединение с БД. Строки возвращаются как словари."""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db(retries: int = 10) -> None:
    """
    Создаёт таблицы из schema.sql. С ретраями — на случай, если Postgres
    в Docker ещё поднимается.
    """
    schema = SCHEMA_FILE.read_text(encoding="utf-8")
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            with get_conn() as conn:
                conn.execute(schema)
                conn.commit()
            return
        except psycopg.OperationalError as err:  # БД ещё не готова
            last_error = err
            time.sleep(1.5)
    raise RuntimeError(f"Не удалось подключиться к БД: {last_error}")

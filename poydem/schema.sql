-- Схема БД проекта «Пойдём?».

-- Каталог событий Афиши. Данные события храним целиком в JSONB —
-- так структура совпадает с тем, что отдаёт парсер, без ручного маппинга колонок.
CREATE TABLE IF NOT EXISTS events (
    id   TEXT PRIMARY KEY,
    data JSONB NOT NULL
);

-- Сгенерированные открытки. Текст и метаданные — здесь, сама картинка —
-- файлом в static/cards/, а в БД хранится только её имя (image_file).
CREATE TABLE IF NOT EXISTS cards (
    id           TEXT PRIMARY KEY,
    event_id     TEXT,
    recipient    TEXT,
    relationship TEXT,
    tone         TEXT,
    style        TEXT,
    bg           TEXT,
    message      TEXT,         -- текст открытки (от ИИ)
    image_file   TEXT,         -- имя PNG-файла в static/cards/ (может быть NULL)
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

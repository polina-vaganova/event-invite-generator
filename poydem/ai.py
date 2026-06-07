"""
ИИ-генерация текста открытки через внешний ИИ-API
(OpenAI-совместимый формат chat/completions).

Провайдера и модель можно заменить на любые — настройки в .env:
    OPENROUTER_API_KEY=...      ключ доступа к ИИ-API
    OPENROUTER_MODEL=...        slug модели LLM (опционально)

Картинку рисует ОТДЕЛЬНАЯ функция — image.generate_image() (см. poydem/image.py).
"""
import os
import re

import requests

from . import content

import time

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemma-4-31b-it:free"

# Запасные модели на случай, если основная перегружена (429).
# Бесплатные модели часто заняты — фолбэк делает текст надёжным.
FALLBACK_MODELS = [
    "z-ai/glm-4.5-air:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
]


# ---------- Вызов LLM ----------
def complete(prompt: str) -> str:
    """
    Отправляет промпт в ИИ-API и возвращает текст ответа.
    Пробует основную модель, при перегрузке (429) — ретраи и запасные модели.
    """
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("Нет ключа ИИ-API. Задайте OPENROUTER_API_KEY в .env")

    primary = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
    models = [primary] + [m for m in FALLBACK_MODELS if m != primary]
    last_error = "неизвестно"

    for model in models:
        for _ in range(2):  # ретрай на 429
            resp = requests.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "X-Title": "Poydem",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 1.0,  # творческая случайность → фразы различаются
                },
                timeout=45,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
            last_error = f"{resp.status_code}: {resp.text[:200]}"
            if resp.status_code == 429:
                time.sleep(2)
                continue
            break  # не-429 ошибка → пробуем следующую модель

    raise RuntimeError(f"ИИ-сервис недоступен ({last_error})")


# ---------- Промпт для текста ----------
STYLE_GUIDE = {
    "friendly": "молодёжно и неформально, со сленгом (го, погнали); очень коротко — 2–4 слова, задорно; мемность приветствуется",
    "romantic": "нежно и романтично, на «ты», тепло и чувственно, с лёгким флиртом; БЕЗ сленга и мемов; коротко — до 7 слов",
    "family": "тепло и по-семейному, душевно и уютно, по-доброму; БЕЗ сленга и мемов, без «го/погнали»; коротко — до 7 слов",
    "funny": "мемно и по-молодёжному, со сленгом и шуткой (умоляю, это будет ор, не сливайся); очень коротко — 2–5 слов",
}


def build_prompt(event: dict, recipient: str, style: str) -> str:
    """Собирает промпт для LLM из события, получателя и стиля."""
    title = event.get("title", "событие")
    name = (recipient or "").strip() or "друг"
    tone = STYLE_GUIDE.get(style, STYLE_GUIDE["friendly"])

    return (
        "Ты придумываешь короткую фразу-подпись для открытки-приглашения.\n\n"
        f"Событие: «{title}» (категория: {event.get('category', '')}).\n"
        f"Кого зовём: {name}.\n"
        f"Тон: {tone}.\n\n"
        "Правила:\n"
        "- СТРОГО следуй тону выше — он задаёт и длину, и допустимость сленга/мемов;\n"
        f"- это короткая фраза-подпись, а НЕ описание; обратись по имени «{name}»;\n"
        f"- используй ИМЕННО имя «{name}», НЕ пиши заглушки в скобках вроде [Имя] или [имя];\n"
        "- варианты разных тонов должны явно отличаться по настроению;\n"
        "- НЕ пиши дату, время, место и название — они будут отдельно;\n"
        "- БЕЗ эмодзи и смайликов;\n"
        "- ОДНА-ЕДИНСТВЕННАЯ фраза — НЕ список, НЕ несколько вариантов, без переносов строк;\n"
        "- верни ТОЛЬКО эту фразу — без пояснений, заголовков и кавычек.\n"
    )


def _one_phrase(text: str) -> str:
    """Берёт одну фразу: первую непустую строку, без кавычек и маркеров списка."""
    for raw in (text or "").splitlines():
        line = raw.strip().lstrip("-•*0123456789.) ").strip(' "«»\'')
        if line:
            return line
    return (text or "").strip()


def _fix_name(text: str, recipient: str) -> str:
    """Подстраховка: меняет заглушку [Имя]/[имя]/[name] на реальное имя."""
    name = (recipient or "").strip()
    if not name:
        return re.sub(r"\[[^\]]*\]\s*,?\s*", "", text).strip()
    return re.sub(r"\[[^\]]*\]", name, text).strip()


def generate_card_text(event: dict, recipient: str, style: str) -> str:
    """
    Текст открытки. Если есть ключ ИИ-API — зовёт LLM,
    иначе (или при ошибке) — заглушка по стилю, чтобы продукт не падал.
    """
    if os.environ.get("OPENROUTER_API_KEY"):
        try:
            return _fix_name(_one_phrase(complete(build_prompt(event, recipient, style))), recipient)
        except Exception:  # noqa: BLE001 — на демо не падаем, откатываемся на заглушку
            pass
    return content.draft_message(recipient, style)


# ============================================================
# ПРОМПТ ДЛЯ КАРТИНКИ — его пишет САМА нейросеть (LLM)
# ============================================================

# 🎨 НАШИ ПОЖЕЛАНИЯ К РИСУНКУ — правь это под себя (на русском).
# Опиши, как должны выглядеть открытки: стиль рисунка, цвета, атмосферу.
IMAGE_STYLE = (
    "милая рисованная иллюстрация в стиле стикеров, минималистичная, "
    "немного мемная и забавная, добрый юмор; "
    "один или несколько милых персонажей-маскотов (НЕ толпа), крупно, "
    "в смешной или неожиданной ситуации; "
    "простой однотонный светлый фон (один цвет, чтобы легко вырезать); "
    "мягкие плавные формы, лёгкие тени, минимум деталей"
)

# Тон под стиль коммуникации (подсказка нейросети для настроения картинки).
STYLE_MOOD = {
    "friendly": "дружеская, тёплая, приглашающая",
    "romantic": "романтичная, нежная, интимная",
    "family": "уютная, семейная, душевная",
    "funny": "игривая, весёлая, с юмором",
}

# Фолбэк-визуал по категории, если LLM недоступен.
CATEGORY_VISUAL = {
    "movie": "cinematic movie scene, dramatic lighting",
    "concert": "vibrant concert stage, bright lights, energetic crowd",
    "performance": "elegant theatre stage, red curtains, spotlight",
    "exhibition": "art gallery interior, paintings, refined atmosphere",
    "restaurant": "cozy restaurant table, warm candle light",
}


def build_image_prompt(event: dict, style: str) -> str:
    """
    Просит нейросеть (LLM) составить АНГЛИЙСКИЙ промпт для картинки,
    учитывая контекст события и наши пожелания (IMAGE_STYLE).
    Если LLM недоступен — фолбэк на простой шаблон.
    """
    mood = STYLE_MOOD.get(style, STYLE_MOOD["friendly"])
    description = (event.get("description") or "")[:400]

    instruction = (
        "Ты — арт-директор. Составь промпт НА АНГЛИЙСКОМ для нейросети-художника, "
        "которая нарисует иллюстрацию для открытки-приглашения на событие.\n\n"
        f"Событие: «{event.get('title', '')}» (категория: {event.get('category', '')}).\n"
        f"Место: {event.get('venue', '')}\n"
        f"Описание: {description}\n"
        f"Настроение открытки: {mood}.\n\n"
        f"Наши пожелания к рисунку: {IMAGE_STYLE}\n\n"
        "Правила:\n"
        "- ответь ТОЛЬКО промптом на английском, одной строкой;\n"
        "- придумай одного или нескольких (но НЕ толпу) милых забавных "
        "персонажей-маскотов, связанных с сутью события и местом, в игривой ситуации;\n"
        "- персонаж(и) крупно по центру, с насыщенными цветами и чёткой тёмной обводкой, "
        "на простом однотонном фоне, КОНТРАСТНОМ к персонажу (не белый персонаж на белом фоне);\n"
        "- учти наши пожелания (стиль рисунка, цвета) и настроение;\n"
        "- в конце обязательно добавь: bold clean outline, saturated colors, plain solid contrasting background, no text, no letters, no watermark;\n"
        "- без кавычек, заголовков и пояснений."
    )

    try:
        return complete(instruction)
    except Exception:  # noqa: BLE001 — фолбэк, если LLM недоступен
        base = CATEGORY_VISUAL.get(event.get("category"), "festive event scene")
        return f"{base}, greeting card illustration, vivid colors, no text, no letters"

"""
ИИ-генерация текста открытки через OpenRouter (бесплатные модели LLM).

Нужен ключ в .env:
    OPENROUTER_API_KEY=...
    OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free   (опционально)

Как получить ключ: https://openrouter.ai → Sign in → Keys → Create Key.
Бесплатные модели ищи на https://openrouter.ai/models (фильтр «Free»).

Картинку рисует ОТДЕЛЬНАЯ функция — image.generate_image() (см. poydem/image.py).
"""
import os

import requests

from . import content

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "qwen/qwen3-next-80b-a3b-instruct:free"


# ---------- Вызов LLM ----------
def complete(prompt: str) -> str:
    """
    Отправляет промпт в OpenRouter и возвращает текст ответа.
    Бросает понятную ошибку, если нет ключа или API не ответил.
    """
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("Нет ключа OpenRouter. Задайте OPENROUTER_API_KEY в .env")

    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
    resp = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Title": "Poydem",
        },
        json={"model": model, "messages": [{"role": "user", "content": prompt}]},
        timeout=40,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"OpenRouter вернул {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


# ---------- Промпт для текста ----------
STYLE_GUIDE = {
    "friendly": "по-дружески, на «ты», тепло и непринуждённо, с лёгким задором — как зовёшь близкого друга",
    "romantic": "романтично, на «ты», нежно и чувственно, с лёгким флиртом — как зовёшь любимого человека",
    "family": "по-семейному, тепло и по-домашнему, уютно — как зовёшь родных",
    "funny": "с юмором, легко и игриво, можно лёгкую шутку или весёлое преувеличение",
}


def build_prompt(event: dict, recipient: str, style: str) -> str:
    """Собирает промпт для LLM из события, получателя и стиля."""
    title = event.get("title", "событие")
    name = (recipient or "").strip() or "друг"
    tone = STYLE_GUIDE.get(style, STYLE_GUIDE["friendly"])
    details = ", ".join(p for p in [event.get("date"), event.get("venue")] if p)
    when_where = f" ({details})" if details else ""

    return (
        "Ты придумываешь короткий текст для открытки-приглашения на событие.\n\n"
        f"Событие: «{title}»{when_where}.\n"
        f"Кого зовём: {name}.\n"
        f"Тон: {tone}.\n\n"
        "Напиши приглашение на русском языке по правилам:\n"
        "- 2–3 коротких предложения;\n"
        "- обратись к получателю по имени;\n"
        "- естественно упомяни событие, по-человечески, не сухо;\n"
        "- выдержи заданный тон;\n"
        "- добавь 1–2 уместных эмодзи;\n"
        "- не выдумывай фактов: дату и место бери только из данных выше;\n"
        "- верни ТОЛЬКО текст открытки — без пояснений, заголовков и кавычек вокруг.\n"
    )


def generate_card_text(event: dict, recipient: str, style: str) -> str:
    """
    Текст открытки. Если есть ключ OpenRouter — зовёт LLM,
    иначе (или при ошибке) — заглушка по стилю, чтобы продукт не падал.
    """
    if os.environ.get("OPENROUTER_API_KEY"):
        try:
            return complete(build_prompt(event, recipient, style))
        except Exception:  # noqa: BLE001 — на демо не падаем, откатываемся на заглушку
            pass
    return content.draft_message(recipient, style)


# ============================================================
# ПРОМПТ ДЛЯ КАРТИНКИ — место для логики команды
# ============================================================
# Здесь команда задаёт, как картинка зависит от ваших предпочтений и события.
# Ниже — простой рабочий пример-заглушка, замените на свои правила.

CATEGORY_VISUAL = {
    "movie": "cinematic movie scene, dramatic lighting",
    "concert": "vibrant concert stage, bright lights, energetic crowd",
    "performance": "elegant theatre stage, red curtains, spotlight",
    "exhibition": "art gallery interior, paintings on walls, refined atmosphere",
    "restaurant": "cozy restaurant table, warm candle light, fine dining",
}

STYLE_MOOD = {
    "friendly": "fun and warm inviting mood",
    "romantic": "romantic soft intimate mood",
    "family": "cozy heartwarming family-friendly mood",
    "funny": "playful quirky humorous mood",
}


def build_image_prompt(event: dict, style: str) -> str:
    """
    АНГЛИЙСКИЙ промпт для нейросети-художника (FLUX). Без текста на картинке.

    TODO (команда): заменить тело на свою логику — как картинка зависит от
    предпочтений и события. Сигнатуру можно расширить.
    """
    base = CATEGORY_VISUAL.get(event.get("category"), "festive event scene")
    mood = STYLE_MOOD.get(style, STYLE_MOOD["friendly"])
    return (
        f"{base}, {mood}, greeting card illustration, vivid colors, "
        "high quality, no text, no letters"
    )

"""
ИИ-генерация текста открытки.

СЕЙЧАС generate_card_text() — заглушка (content.draft_message).
Промпт для модели уже готов: build_prompt(). Команде остаётся подставить
вызов LLM в generate_card_text() — промпт менять не нужно.

Картинку рисует ОТДЕЛЬНАЯ функция — image.generate_image() (см. poydem/image.py).
"""
from . import content

# Описание тона под каждый стиль коммуникации (из кейса).
STYLE_GUIDE = {
    "friendly": "по-дружески, на «ты», тепло и непринуждённо, с лёгким задором — как зовёшь близкого друга",
    "romantic": "романтично, на «ты», нежно и чувственно, с лёгким флиртом — как зовёшь любимого человека",
    "family": "по-семейному, тепло и по-домашнему, уютно — как зовёшь родных",
    "funny": "с юмором, легко и игриво, можно лёгкую шутку или весёлое преувеличение",
}


def build_prompt(event: dict, recipient: str, style: str) -> str:
    """
    Собирает промпт для LLM из события, получателя и стиля.
    Возвращает готовую строку-инструкцию для модели.
    """
    title = event.get("title", "событие")
    name = (recipient or "").strip() or "друг"
    tone = STYLE_GUIDE.get(style, STYLE_GUIDE["friendly"])

    # Дату и место подставляем, только если они есть (не выдумываем).
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


# Базовый визуал под категорию события (для картинки).
CATEGORY_VISUAL = {
    "movie": "cinematic movie scene, dramatic lighting",
    "concert": "vibrant concert stage, bright lights, energetic crowd",
    "performance": "elegant theatre stage, red curtains, spotlight",
    "exhibition": "art gallery interior, paintings on walls, refined atmosphere",
    "restaurant": "cozy restaurant table, warm candle light, fine dining",
}

# Настроение под стиль коммуникации (для картинки).
STYLE_MOOD = {
    "friendly": "fun and warm inviting mood",
    "romantic": "romantic soft intimate mood",
    "family": "cozy heartwarming family-friendly mood",
    "funny": "playful quirky humorous mood",
}


def build_image_prompt(event: dict, style: str) -> str:
    """
    Собирает АНГЛИЙСКИЙ промпт для нейросети-художника (FLUX).
    Без текста на картинке — буквы модель рисует плохо.
    """
    base = CATEGORY_VISUAL.get(event.get("category"), "festive event scene")
    mood = STYLE_MOOD.get(style, STYLE_MOOD["friendly"])
    return (
        f"{base}, {mood}, greeting card illustration, vivid colors, "
        "high quality, no text, no letters"
    )


def generate_card_text(event: dict, recipient: str, style: str) -> str:
    """
    Возвращает текст открытки.

    TODO (команда): заменить заглушку на вызов LLM.
    Промпт уже готов — build_prompt(). Пример (псевдокод):

        prompt = build_prompt(event, recipient, style)
        return call_llm(prompt).strip()   # ваш вызов Gemini / Cloudflare / ...
    """
    # --- ЗАГЛУШКА (пока без модели) ---
    return content.draft_message(recipient, style)

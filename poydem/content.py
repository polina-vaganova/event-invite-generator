"""
Справочники и заглушки контента: категории событий, стили открытки, цвета,
тон приглашения, а также ЗАГЛУШКА генерации текста (вместо ИИ).

Когда подключите ИИ — замените draft_message() на вызов модели в ai.py,
остальной код и шаблоны не изменятся.
"""

# --- Категории событий Афиши ---
CATEGORY_LABELS = {
    "movie": ("Кино", "🎬"),
    "concert": ("Концерт", "🎵"),
    "performance": ("Спектакль", "🎭"),
    "theatre": ("Спектакль", "🎭"),
    "exhibition": ("Выставка", "🖼"),
    "restaurant": ("Ресторан", "🍽"),
}


def category_label(category: str) -> tuple[str, str]:
    """Возвращает (подпись, эмодзи) для категории."""
    return CATEGORY_LABELS.get(category, ("Событие", "✨"))


# --- Шаг 1: стиль открытки ---
CARD_STYLES = [
    {"id": "festive", "label": "Праздничный", "emoji": "🎂"},
    {"id": "minimal", "label": "Минимализм", "emoji": "⚪"},
    {"id": "meme", "label": "Мемный", "emoji": "⭐"},
    {"id": "tender", "label": "Нежный", "emoji": "☁️"},
]

# Цвета фона открытки. light=True → фон тёмный, текст белый.
BG_COLORS = [
    {"id": "lime", "hex": "#d6f24a", "light": False},
    {"id": "gray", "hex": "#e6e6e9", "light": False},
    {"id": "purple", "hex": "#7c3aed", "light": True},
    {"id": "blue", "hex": "#4f7df0", "light": True},
    {"id": "olive", "hex": "#9aa86a", "light": False},
    {"id": "peach", "hex": "#f3c8a6", "light": False},
    {"id": "lavender", "hex": "#d9c9f2", "light": False},
]

STICKERS = ["🎈", "💜", "⭐", "☁️", "🎉", "🎂", "💚", "✨", "🔥", "🥂"]

# --- Шаг 2: отношения и тон ---
RELATIONSHIPS = [
    {"id": "friends", "label": "Друзья", "emoji": "🤝"},
    {"id": "couple", "label": "Пара", "emoji": "💕"},
    {"id": "colleagues", "label": "Коллеги", "emoji": "💼"},
    {"id": "family", "label": "Семья", "emoji": "🏡"},
]

TONES = [
    {"id": "fun", "label": "Весёлый", "emoji": "😄"},
    {"id": "warm", "label": "Тёплый", "emoji": "🤗"},
    {"id": "romantic", "label": "Романтичный", "emoji": "💕"},
    {"id": "creative", "label": "Креативный", "emoji": "🎨"},
]


def draft_message(recipient: str, tone: str) -> str:
    """
    ЗАГЛУШКА генерации текста открытки под выбранный тон.

    TODO (команда): заменить на вызов ИИ в ai.py — учесть получателя,
    отношения, событие и доп. пожелания.
    """
    name = (recipient or "").strip() or "Привет"
    by_tone = {
        "fun": f"{name}! Празднуем это так, как ты любишь — громко, душевно и до утра! 🎉",
        "warm": f"{name}, давно хотел позвать тебя. Будет тепло и по-нашему 💛",
        "romantic": f"{name}, проведём этот вечер вдвоём? Только ты и я ✨",
        "creative": f"{name}, у меня идея на вечер — и без тебя она не считается 🚀",
    }
    return by_tone.get(tone, by_tone["fun"])

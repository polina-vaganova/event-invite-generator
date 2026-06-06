"""
Справочники и заглушка текста открытки.

По кейсу нужен минимум: получатель + стиль коммуникации. Стили названы
ровно как в кейсе: романтичный, дружеский, семейный, шуточный.

Когда подключите ИИ — замените draft_message() на вызов модели в ai.py.
"""

# --- Категории событий Афиши (для подписей в каталоге) ---
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


# --- Стиль коммуникации (дословно из кейса) ---
COMM_STYLES = [
    {"id": "friendly", "label": "Дружеский", "emoji": "🤝"},
    {"id": "romantic", "label": "Романтичный", "emoji": "💕"},
    {"id": "family", "label": "Семейный", "emoji": "🏡"},
    {"id": "funny", "label": "Шуточный", "emoji": "😄"},
]


def draft_message(recipient: str, style: str) -> str:
    """
    ЗАГЛУШКА генерации текста открытки под выбранный стиль коммуникации.

    TODO (команда): заменить на вызов ИИ в ai.py.
    """
    name = (recipient or "").strip() or "Привет"
    by_style = {
        "romantic": f"{name}, только ты и я ✨",
        "friendly": f"{name}, го? 🎉",
        "family": f"{name}, идём вместе 💛",
        "funny": f"{name}, умоляю 🔥",
    }
    return by_style.get(style, by_style["friendly"])

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
# icon — путь к картинке в static/ (если задан, показываем её вместо emoji)
COMM_STYLES = [
    {"id": "friendly", "label": "Дружеский", "emoji": "🤝", "icon": "icons/friendly.png"},
    {"id": "romantic", "label": "Романтичный", "emoji": "💕", "icon": "icons/romantic.png"},
    {"id": "family", "label": "Семейный", "emoji": "🏡", "icon": "icons/family.png"},
    {"id": "funny", "label": "Шуточный", "emoji": "😄", "icon": "icons/funny.png"},
]


def draft_message(recipient: str, style: str) -> str:
    """
    ЗАГЛУШКА генерации текста открытки под выбранный стиль коммуникации.

    TODO (команда): заменить на вызов ИИ в ai.py.
    """
    name = (recipient or "").strip() or "Привет"
    by_style = {
        "romantic": f"{name}, этот вечер — для нас двоих",
        "friendly": f"{name}, го?",
        "family": f"{name}, проведём время всей семьёй",
        "funny": f"{name}, умоляю, не сливайся",
    }
    return by_style.get(style, by_style["friendly"])

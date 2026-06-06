"""
ИИ-генерация текста открытки.

СЕЙЧАС ЗАГЛУШКА: возвращает шаблонный текст из content.draft_message().

TODO (команда, направление «ИИ»):
  1. Выбрать ИИ-API (GigaChat / OpenAI / YandexGPT) и положить ключ в .env.
  2. В generate_card_text() собрать промпт из аргументов и вызвать модель.
  3. Вернуть готовый текст. Шаблоны и фронтенд менять НЕ нужно — они зовут
     эту функцию через эндпоинт /api/generate.

Пример промпта:
  «Напиши короткое приглашение (2–3 предложения) на событие "{event[title]}"
   ({event[date]}, {event[venue]}). Получатель: {recipient}. Стиль: {style}
   (романтичный / дружеский / семейный / шуточный). По-русски, по-человечески,
   с уместным эмодзи.»
"""
from . import content


def generate_card_text(event: dict, recipient: str, style: str) -> str:
    """
    Возвращает текст открытки.

    Пока — заглушка по стилю. Когда подключите ИИ, замените тело этой функции
    на вызов модели, сохранив сигнатуру.
    """
    # --- ЗАГЛУШКА ---
    return content.draft_message(recipient, style)

    # --- ПРИМЕР будущей реализации (раскомментировать и доработать) ---
    # prompt = build_prompt(event, recipient, style)
    # return call_ai_model(prompt).strip()   # ваш вызов GigaChat/OpenAI

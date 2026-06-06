"""
ИИ-генерация текста открытки.

СЕЙЧАС ЗАГЛУШКА: возвращает шаблонный текст из content.draft_message().

TODO (команда, направление «ИИ»):
  1. Выбрать ИИ-API (GigaChat / OpenAI / YandexGPT) и положить ключ в .env.
  2. В generate_card_text() собрать промпт из аргументов и вызвать модель.
  3. Вернуть готовый текст. Шаблоны и фронтенд менять НЕ нужно — они уже
     зовут эту функцию через эндпоинт /api/generate.

Пример промпта (псевдокод):
  «Ты пишешь короткое тёплое приглашение на событие. Событие: {event[title]}
   ({event[date]}, {event[venue]}). Получатель: {recipient}. Отношения:
   {relationship}. Тон: {tone}. Доп. пожелания: {details}. 2–3 предложения,
   на русском, по-человечески, с уместным эмодзи.»
"""
from . import content


def generate_card_text(
    event: dict,
    recipient: str,
    relationship: str,
    tone: str,
    details: str = "",
    extra: str = "",
) -> str:
    """
    Возвращает текст открытки.

    Пока — заглушка по тону. Когда подключите ИИ, замените тело этой функции
    на вызов модели, сохранив сигнатуру.
    """
    # --- ЗАГЛУШКА ---
    return content.draft_message(recipient, tone)

    # --- ПРИМЕР будущей реализации (раскомментировать и доработать) ---
    # prompt = build_prompt(event, recipient, relationship, tone, details, extra)
    # response = call_ai_model(prompt)   # ваш вызов GigaChat/OpenAI
    # return response.strip()

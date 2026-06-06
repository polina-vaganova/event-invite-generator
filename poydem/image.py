"""
Генерация картинки нейросетью через OpenRouter (modalities: ["image"]).

Использует ТОТ ЖЕ ключ, что и текст:
    OPENROUTER_API_KEY=...
    OPENROUTER_IMAGE_MODEL=...   (модель-художник; выбери бесплатную, см. ниже)

⚠️ Картинки на OpenRouter — это ОТДЕЛЬНЫЕ модели (вкладка Image).
Бесплатные помечены значком подарка 🎁. Выбери бесплатную и впиши её slug
в OPENROUTER_IMAGE_MODEL, иначе будет ошибка оплаты.
"""
import base64
import os

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_IMAGE_MODEL = "x-ai/grok-imagine-image-quality"


def generate_image(prompt: str) -> bytes:
    """
    Рисует картинку по описанию и возвращает её байты.
    Бросает понятную ошибку, если нет ключа или модель не вернула картинку.
    """
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("Нет ключа OpenRouter. Задайте OPENROUTER_API_KEY в .env")

    model = os.environ.get("OPENROUTER_IMAGE_MODEL", DEFAULT_IMAGE_MODEL)
    resp = requests.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["image"],
        },
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"OpenRouter вернул {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    images = (data.get("choices") or [{}])[0].get("message", {}).get("images")
    if not images:
        raise RuntimeError(f"В ответе нет картинки: {str(data)[:300]}")

    # Картинка приходит как data-URL: "data:image/png;base64,XXXX"
    url = images[0]["image_url"]["url"]
    b64 = url.split(",", 1)[1] if "," in url else url
    return base64.b64decode(b64)

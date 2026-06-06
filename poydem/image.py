"""
Генерация картинки нейросетью через OpenRouter (modalities: ["image"]).

Используется ТОТ ЖЕ ключ, что и текст (OPENROUTER_API_KEY) — один ключ на всё.
Модель — бесплатная Sourceful Riverflow (free).

⚠️ ВНИМАНИЕ: бесплатные Riverflow помечены на OpenRouter «Going away 9 June 2026».
Если перестанут работать — выбери другую бесплатную модель во вкладке Image
(значок 🎁) и впиши её в OPENROUTER_IMAGE_MODEL, либо переключись на
Cloudflare Workers AI (FLUX) как бесплатный бэкап.
"""
import base64
import os

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_IMAGE_MODEL = "sourceful/riverflow-v2.5-fast:free"


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
        timeout=90,
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

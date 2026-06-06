"""
Генерация картинки нейросетью через Cloudflare Workers AI (модель FLUX.1 schnell).

Нужны ключи в .env:
    CLOUDFLARE_ACCOUNT_ID=...
    CLOUDFLARE_API_TOKEN=...

Как получить: https://dash.cloudflare.com → API Tokens (шаблон «Workers AI») + Account ID.
Бесплатный тариф: 10 000 «нейронов»/день (~100–200 картинок), без карты.
"""
import base64
import os

import requests

MODEL = "@cf/black-forest-labs/flux-1-schnell"


def generate_image(prompt: str, steps: int = 6) -> bytes:
    """
    Рисует картинку по описанию и возвращает байты PNG/JPEG.
    Бросает понятную ошибку, если ключей нет или API не ответил.
    """
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not account_id or not token:
        raise RuntimeError(
            "Нет ключей Cloudflare. Задайте CLOUDFLARE_ACCOUNT_ID и "
            "CLOUDFLARE_API_TOKEN в файле .env"
        )

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{MODEL}"
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": prompt, "steps": steps},
        timeout=40,
    )

    if resp.status_code != 200:
        raise RuntimeError(f"Cloudflare вернул {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    # FLUX.1 schnell отдаёт картинку как base64 в result.image
    b64 = (data.get("result") or {}).get("image")
    if not b64:
        raise RuntimeError(f"В ответе нет картинки: {str(data)[:300]}")

    return base64.b64decode(b64)

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
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image"],
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    last_err = None
    for attempt in range(2):  # повтор при обрыве/таймауте (модель бывает медленной)
        try:
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=120)
        except requests.exceptions.RequestException as err:
            last_err = err
            continue
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

    raise RuntimeError(
        "Картинка не сгенерировалась — модель не ответила вовремя. Попробуйте ещё раз."
    )


def remove_background(img_bytes: bytes) -> bytes:
    """
    Убирает фон у картинки → прозрачный PNG (через rembg, локально, бесплатно).
    При первом запуске rembg скачает модель (~170 МБ), дальше работает офлайн.

    Защита: если светлый персонаж на светлом фоне и rembg вырезал почти всё —
    возвращаем исходную картинку (лучше видимый персонаж, чем пустая открытка).
    """
    import io

    from PIL import Image
    from rembg import remove  # ленивый импорт — библиотека тяжёлая

    cut = remove(img_bytes, post_process_mask=True)
    im = Image.open(io.BytesIO(cut)).convert("RGBA")
    # доля непрозрачных пикселей (alpha > ~40)
    opaque = sum(im.getchannel("A").histogram()[40:])
    if opaque < 0.04 * im.width * im.height:
        return img_bytes  # вырезалось почти всё → отдаём оригинал
    return cut


def generate_card_image(prompt: str) -> bytes:
    """Рисует картинку и убирает фон → прозрачный PNG персонажа для открытки."""
    return remove_background(generate_image(prompt))

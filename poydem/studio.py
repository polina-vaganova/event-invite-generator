"""
Blueprint студии открыток (наш продукт).

  • GET  /create?event=<id>  — экран создания открытки (получает событие по ID)
  • POST /api/generate       — генерация текста открытки (сейчас заглушка, потом ИИ)
"""
import random
from pathlib import Path

from flask import (
    Blueprint, render_template, request, jsonify, Response, url_for, current_app, abort,
)

from . import store, content, ai, image, cards, card_render

bp = Blueprint("studio", __name__)


@bp.get("/api/test-image")
def api_test_image():
    """
    Проверка ключей Cloudflare: рисует картинку по ?prompt=... и отдаёт её.
    Пример: /api/test-image?prompt=festive concert neon vibrant
    """
    prompt = request.args.get("prompt", "cute mascot character, sticker style, plain background, no text")
    try:
        img = image.generate_card_image(prompt)  # генерация + удаление фона
        return Response(img, mimetype="image/png")
    except Exception as err:  # noqa: BLE001
        return jsonify({"error": str(err)}), 502


@bp.get("/api/test-text")
def api_test_text():
    """
    Проверка ключа OpenRouter: генерит текст приглашения и отдаёт его.
    Пример: /api/test-text?recipient=Аня&style=friendly&event=6014552
    """
    event = store.get_event(request.args.get("event", "")) or {
        "title": "Баста",
        "date": "29 августа 2026, 19:00",
        "venue": "Лужники",
    }
    try:
        prompt = ai.build_prompt(event, request.args.get("recipient", "Аня"),
                                 request.args.get("style", "friendly"))
        return jsonify({"text": ai.complete(prompt)})
    except Exception as err:  # noqa: BLE001
        return jsonify({"error": str(err)}), 502


@bp.get("/create")
def create():
    """Студия открытки. Событие берётся по ID — как из API Афиши."""
    event_id = request.args.get("event")
    event = store.get_event(event_id) if event_id else None
    return render_template(
        "studio/create.html",
        event=event,
        comm_styles=content.COMM_STYLES,
    )


@bp.post("/api/card")
def api_card():
    """
    Полная сборка открытки: текст (ИИ) + персонаж (ИИ, прозрачный) + инфо события
    → одна картинка-открытка (Pillow). Сохраняет в БД и файл.
    Тело: { event_id, recipient, style }
    Возвращает: { card_id, url, text }
    """
    data = request.get_json(silent=True) or {}
    event = store.get_event(data.get("event_id"))
    if not event:
        return jsonify({"error": "Событие не найдено"}), 404

    recipient = data.get("recipient", "")
    style = data.get("style", "friendly")

    bg = random.choice(list(card_render.PALETTE))  # случайный фон по умолчанию
    try:
        # 1. текст 2. персонаж (прозрачный PNG) 3. сборка открытки
        text = ai.generate_card_text(event, recipient, style)
        character = image.generate_card_image(ai.build_image_prompt(event, style))
        card_png = card_render.render_card(event, text, character, bg=bg)
    except Exception as err:  # noqa: BLE001
        return jsonify({"error": str(err)}), 502

    # сохраняем картинку + персонажа (для пересборки с другим фоном) + строку в БД
    card_id = cards.new_card_id()
    cards_dir = Path(current_app.static_folder) / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{card_id}.png"
    (cards_dir / filename).write_bytes(card_png)
    (cards_dir / f"{card_id}_char.png").write_bytes(character)  # прозрачный персонаж
    cards.save_card(card_id, event["id"], recipient, style, text, filename)

    return jsonify({
        "card_id": card_id,
        "url": url_for("static", filename=f"cards/{filename}"),
        "text": text,
        "color": bg,
        "colors": list(card_render.PALETTE.keys()),
    })


@bp.post("/api/recolor")
def api_recolor():
    """
    Пересобрать готовую открытку с другим фоном — БЕЗ повторной генерации ИИ.
    Тело: { card_id, color }
    Возвращает: { url }
    """
    data = request.get_json(silent=True) or {}
    item = cards.get_card(data.get("card_id"))
    if not item:
        return jsonify({"error": "Открытка не найдена"}), 404

    cards_dir = Path(current_app.static_folder) / "cards"
    char_path = cards_dir / f"{item['id']}_char.png"
    if not char_path.exists():
        return jsonify({"error": "Нет исходного персонажа"}), 404

    event = store.get_event(item["event_id"]) or {}
    card_png = card_render.render_card(
        event, item["message"], char_path.read_bytes(), bg=data.get("color", "pink"),
    )
    (cards_dir / item["image_file"]).write_bytes(card_png)
    return jsonify({"url": url_for("static", filename=f"cards/{item['image_file']}")})


@bp.get("/card/<card_id>")
def card(card_id: str):
    """Страница открытки для получателя: картинка + кнопка обратно на событие."""
    item = cards.get_card(card_id)
    if not item:
        abort(404)
    event = store.get_event(item["event_id"]) or {}
    image_url = url_for("static", filename=f"cards/{item['image_file']}")
    return render_template("studio/card.html", card=item, event=event, image_url=image_url)

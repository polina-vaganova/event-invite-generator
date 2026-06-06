"""
Blueprint студии открыток (наш продукт).

  • GET  /create?event=<id>  — экран создания открытки (получает событие по ID)
  • POST /api/generate       — генерация текста открытки (сейчас заглушка, потом ИИ)
"""
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

    try:
        # 1. текст 2. персонаж (прозрачный PNG) 3. сборка открытки
        text = ai.generate_card_text(event, recipient, style)
        character = image.generate_card_image(ai.build_image_prompt(event, style))
        card_png = card_render.render_card(event, text, character)
    except Exception as err:  # noqa: BLE001
        return jsonify({"error": str(err)}), 502

    # сохраняем картинку файлом + строку в БД
    card_id = cards.new_card_id()
    cards_dir = Path(current_app.static_folder) / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{card_id}.png"
    (cards_dir / filename).write_bytes(card_png)
    cards.save_card(card_id, event["id"], recipient, style, text, filename)

    return jsonify({
        "card_id": card_id,
        "url": url_for("static", filename=f"cards/{filename}"),
        "text": text,
    })


@bp.get("/card/<card_id>")
def card(card_id: str):
    """Страница открытки для получателя: картинка + кнопка обратно на событие."""
    item = cards.get_card(card_id)
    if not item:
        abort(404)
    event = store.get_event(item["event_id"]) or {}
    image_url = url_for("static", filename=f"cards/{item['image_file']}")
    return render_template("studio/card.html", card=item, event=event, image_url=image_url)

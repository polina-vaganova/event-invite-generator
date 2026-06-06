"""
Blueprint студии открыток (наш продукт).

  • GET  /create?event=<id>  — экран создания открытки (получает событие по ID)
  • POST /api/generate       — генерация текста открытки (сейчас заглушка, потом ИИ)
"""
from flask import Blueprint, render_template, request, jsonify, Response

from . import store, content, ai, image

bp = Blueprint("studio", __name__)


@bp.get("/api/test-image")
def api_test_image():
    """
    Проверка ключей Cloudflare: рисует картинку по ?prompt=... и отдаёт её.
    Пример: /api/test-image?prompt=festive concert neon vibrant
    """
    prompt = request.args.get("prompt", "festive concert invitation, vibrant, no text")
    try:
        img = image.generate_image(prompt)
        return Response(img, mimetype="image/jpeg")
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


@bp.post("/api/generate")
def api_generate():
    """
    Генерация текста открытки.
    Тело: { event_id, recipient, style }
    Возвращает: { text }
    """
    data = request.get_json(silent=True) or {}
    event = store.get_event(data.get("event_id")) or {}
    text = ai.generate_card_text(
        event=event,
        recipient=data.get("recipient", ""),
        style=data.get("style", ""),
    )
    return jsonify({"text": text})

"""
Blueprint студии открыток (наш продукт).

  • GET  /create?event=<id>  — экран создания открытки (получает событие по ID)
  • POST /api/generate       — генерация текста открытки (сейчас заглушка, потом ИИ)
"""
from flask import Blueprint, render_template, request, jsonify

from . import store, content, ai

bp = Blueprint("studio", __name__)


@bp.get("/create")
def create():
    """Студия открытки. Событие берётся по ID — как из API Афиши."""
    event_id = request.args.get("event")
    event = store.get_event(event_id) if event_id else None
    return render_template(
        "studio/create.html",
        event=event,
        card_styles=content.CARD_STYLES,
        bg_colors=content.BG_COLORS,
        stickers=content.STICKERS,
        relationships=content.RELATIONSHIPS,
        tones=content.TONES,
    )


@bp.post("/api/generate")
def api_generate():
    """
    Генерация текста открытки.
    Тело: { event_id, recipient, relationship, tone, details, extra }
    Возвращает: { text }
    """
    data = request.get_json(silent=True) or {}
    event = store.get_event(data.get("event_id")) or {}
    text = ai.generate_card_text(
        event=event,
        recipient=data.get("recipient", ""),
        relationship=data.get("relationship", ""),
        tone=data.get("tone", ""),
        details=data.get("details", ""),
        extra=data.get("extra", ""),
    )
    return jsonify({"text": text})

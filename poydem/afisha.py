"""
Blueprint мини-Афиши: каталог, страница события, добавление по ссылке, API.

API (GET /api/event/<id>) — это «как будто внутренний API Афиши», которым
пользуется студия открыток, получая событие по ID.
"""
from flask import Blueprint, render_template, request, jsonify, abort

from . import store
from .parser import parse_afisha_event, is_afisha_url, event_id_from_url

bp = Blueprint("afisha", __name__)


# ---------- Страницы ----------
@bp.get("/")
def index():
    """Каталог событий."""
    return render_template("afisha/index.html", events=store.get_all_events())


@bp.get("/event/<event_id>")
def event(event_id: str):
    """Страница события + кнопка «Позвать друга»."""
    item = store.get_event(event_id)
    if item is None:
        abort(404)
    return render_template("afisha/event.html", event=item)


@bp.route("/add", methods=["GET", "POST"])
def add():
    """Добавить событие по ссылке afisha.ru (серверная форма)."""
    error = None
    added = None
    if request.method == "POST":
        url = (request.form.get("url") or "").strip()
        if not is_afisha_url(url):
            error = "Нужна корректная ссылка на событие afisha.ru"
        else:
            # Кэш-первый: если событие уже в каталоге — не дёргаем Афишу
            existing = store.get_event(event_id_from_url(url))
            if existing:
                added = existing
            else:
                try:
                    added = store.add_event(parse_afisha_event(url))
                except Exception as err:  # noqa: BLE001
                    error = str(err)
    return render_template("afisha/add.html", error=error, added=added)


# ---------- API (для студии открыток) ----------
@bp.get("/api/events")
def api_events():
    return jsonify(store.get_all_events())


@bp.get("/api/event/<event_id>")
def api_event(event_id: str):
    item = store.get_event(event_id)
    if item is None:
        return jsonify({"error": "Событие не найдено"}), 404
    return jsonify(item)

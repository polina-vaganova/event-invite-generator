"""
«Пойдём?» — сервис открыток-приглашений на события Афиши.

Одно Flask-приложение с двумя смысловыми частями:
  • Мини-Афиша (декорация + данные)  — blueprint `afisha`
  • Студия открытки (наш продукт)    — blueprint `studio`

Запуск для разработки:  flask --app poydem run --debug --port 5001
"""
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    from . import content
    from .afisha import bp as afisha_bp
    from .studio import bp as studio_bp

    # Хелпер категорий доступен во всех шаблонах
    app.jinja_env.globals["category_label"] = content.category_label

    app.register_blueprint(afisha_bp)
    app.register_blueprint(studio_bp)

    return app


# Удобно для `flask --app poydem run`
app = create_app()

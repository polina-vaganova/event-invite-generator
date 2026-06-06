# «Пойдём?» — команды для запуска проекта.
# Нужны: Python 3.10+ и Docker (для Postgres). Использование: make <команда>

VENV := .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python
FLASK := $(VENV)/bin/flask

.DEFAULT_GOAL := help
.PHONY: help install dev run db-up db-down seed clean

help: ## Показать список команд
	@echo "Команды проекта «Пойдём?»:"
	@echo "  make install  — окружение + зависимости + БД + каталог (первый запуск)"
	@echo "  make dev      — запустить сайт (http://localhost:5001)"
	@echo "  make db-up    — поднять Postgres (Docker)"
	@echo "  make db-down  — остановить Postgres"
	@echo "  make seed     — наполнить каталог из data/events.json"
	@echo "  make clean    — удалить окружение и кэш"

install: ## Первый запуск: venv + зависимости + Postgres + каталог
	test -f .env || cp .env.example .env
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	docker compose up -d
	@echo "Ждём, пока поднимется БД..."
	@sleep 6
	$(PY) -m poydem.seed
	@echo ""
	@echo "Готово! Запуск: make dev"

dev: ## Запустить Flask-сервер с автоперезагрузкой
	@echo "Открой http://localhost:5001"
	$(FLASK) --app poydem run --debug --port 5001

run: dev ## Псевдоним для make dev

db-up: ## Поднять Postgres
	docker compose up -d

db-down: ## Остановить Postgres
	docker compose down

seed: ## Создать таблицы и наполнить каталог из файла
	$(PY) -m poydem.seed

clean: ## Удалить окружение и кэш Python
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} +

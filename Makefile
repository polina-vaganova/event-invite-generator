# «Пойдём?» — команды для запуска проекта.
# Нужен только Python 3.10+. Использование: make <команда>

VENV := .venv
PIP := $(VENV)/bin/pip
FLASK := $(VENV)/bin/flask

.DEFAULT_GOAL := help
.PHONY: help install dev run clean

help: ## Показать список команд
	@echo "Команды проекта «Пойдём?»:"
	@echo "  make install  — создать окружение и поставить зависимости (первый запуск)"
	@echo "  make dev      — запустить сайт (http://localhost:5001)"
	@echo "  make clean    — удалить виртуальное окружение и кэш"

install: ## Создать venv и поставить зависимости
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo ""
	@echo "Готово! Запуск: make dev"

dev: ## Запустить Flask-сервер с автоперезагрузкой
	@echo "Открой http://localhost:5001"
	$(FLASK) --app poydem run --debug --port 5001

run: dev ## Псевдоним для make dev

clean: ## Удалить окружение и кэш Python
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} +

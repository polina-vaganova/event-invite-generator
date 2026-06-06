# «Пойдём?» — команды для быстрого запуска проекта.
# Нужны: Node.js 20+, Docker (запущенный). Использование: make <команда>

.DEFAULT_GOAL := help
.PHONY: help install dev afisha generator db-up db-down seed refresh clean

help: ## Показать список команд
	@echo "Команды проекта «Пойдём?»:"
	@echo "  make install    — установить всё и подготовить БД (первый запуск)"
	@echo "  make dev        — запустить оба сайта: Афиша :3000 + генератор :3001"
	@echo "  make afisha     — только мини-Афиша (:3000)"
	@echo "  make generator  — только генератор (:3001)"
	@echo "  make db-up      — поднять Postgres (Docker)"
	@echo "  make db-down    — остановить Postgres"
	@echo "  make seed       — наполнить каталог из файла (без Афиши)"
	@echo "  make refresh    — обновить каталог из Афиши (редко, осторожно)"

install: ## Первый запуск: зависимости + БД + каталог
	@echo "==> .env файлы"
	cd afisha-mock && { [ -f .env ] || cp .env.example .env; }
	cd generator && { [ -f .env ] || cp .env.example .env; }
	@echo "==> Postgres (Docker)"
	cd afisha-mock && docker compose up -d
	@echo "==> Мини-Афиша: зависимости и БД"
	cd afisha-mock && npm install
	cd afisha-mock && npx prisma migrate deploy && npx prisma generate
	cd afisha-mock && npx tsx scripts/seed.ts
	@echo "==> Генератор: зависимости"
	cd generator && npm install
	@echo ""
	@echo "Готово! Запуск: make dev"

dev: ## Запустить оба сайта одновременно
	@echo "Афиша → http://localhost:3000 | Генератор → http://localhost:3001"
	@echo "(Ctrl+C — остановить оба)"
	cd afisha-mock && npm run dev & \
	cd generator && npm run dev & \
	wait

afisha: ## Запустить только мини-Афишу
	cd afisha-mock && npm run dev

generator: ## Запустить только генератор
	cd generator && npm run dev

db-up: ## Поднять Postgres
	cd afisha-mock && docker compose up -d

db-down: ## Остановить Postgres
	cd afisha-mock && docker compose down

seed: ## Наполнить каталог из prisma/seed-data.json (без Афиши)
	cd afisha-mock && npx tsx scripts/seed.ts

refresh: ## Обновить каталог из Афиши + снимок в seed-data.json
	cd afisha-mock && npx tsx scripts/refresh-catalog.ts
	cd afisha-mock && npx tsx scripts/export-catalog.ts

.PHONY: install dev-backend dev-frontend lint format-check format test build compose-up compose-down

install:
	cd frontend && npm ci
	cd backend && uv sync --dev

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm run dev

lint:
	cd frontend && npm run lint
	cd backend && uv run ruff check .
	cd backend && uv run mypy app

format-check:
	cd frontend && npm run format:check
	cd backend && uv run ruff format --check .

format:
	cd frontend && npm run format
	cd backend && uv run ruff check --fix .
	cd backend && uv run ruff format .

test:
	cd frontend && npm run test
	cd backend && uv run pytest

build:
	cd frontend && npm run build

compose-up:
	docker compose up --build -d

compose-down:
	docker compose down

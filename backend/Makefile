.PHONY: install migrate revision run test seed lint fmt up down

install:
	pip install -r requirements-dev.txt

migrate:
	alembic upgrade head

revision:
	alembic revision --autogenerate -m "$(m)"

run:
	uvicorn app.main:app --reload --port 8000

test:
	pytest

seed:
	python scripts/seed_demo.py

lint:
	ruff check app tests

fmt:
	ruff format app tests

up:
	docker compose up -d db neo4j

down:
	docker compose down

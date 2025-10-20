.PHONY: install run dev lint test format migrate seed

install:
	poetry install --with dev

run:
	poetry run uvicorn city_guide.app.main:app --host ${APP_HOST:-0.0.0.0} --port ${APP_PORT:-8000}

dev:
	poetry run uvicorn city_guide.app.main:app --reload --host ${APP_HOST:-0.0.0.0} --port ${APP_PORT:-8000}

lint:
	poetry run ruff check city_guide && poetry run black --check city_guide && poetry run isort --check city_guide

format:
	poetry run black city_guide && poetry run isort city_guide

test:
	poetry run pytest -q

migrate:
	poetry run alembic upgrade head

seed:
	poetry run python - <<'PY'
from pathlib import Path
from sqlalchemy import create_engine, text
from city_guide.app.core.config import settings
engine = create_engine(settings.sync_database_url)
sql = Path('city_guide/dev/sql/seed_poi_vilnius.sql').read_text()
with engine.begin() as conn:
    conn.execute(text(sql))
PY

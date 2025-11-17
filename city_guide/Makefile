.PHONY: install run dev lint test format migrate seed

PYTHON ?= python3
PROJECT_ROOT := $(abspath $(CURDIR)/..)
APP_HOST ?= 0.0.0.0
APP_PORT ?= 8000

export PYTHONPATH := $(PROJECT_ROOT)

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install --upgrade -r $(PROJECT_ROOT)/.meta/packages

run:
	APP_HOST=$(APP_HOST) APP_PORT=$(APP_PORT) $(PYTHON) -m uvicorn city_guide.app.main:app --host $(APP_HOST) --port $(APP_PORT)

dev:
	APP_HOST=$(APP_HOST) APP_PORT=$(APP_PORT) $(PYTHON) -m uvicorn city_guide.app.main:app --reload --host $(APP_HOST) --port $(APP_PORT)

lint:
	$(PYTHON) -m ruff check city_guide
	$(PYTHON) -m black --check city_guide
	$(PYTHON) -m isort --check-only --profile black --line-length 88 city_guide

format:
	$(PYTHON) -m black city_guide
	$(PYTHON) -m isort --profile black --line-length 88 city_guide

test:
	$(PYTHON) -m pytest -q

migrate:
	$(PYTHON) -m alembic upgrade head

#seed:
#	$(PYTHON) - <<'PY'
#from pathlib import Path
#from sqlalchemy import create_engine, text
#from city_guide.app.core.config import settings
#
#engine = create_engine(settings.sync_database_url)
#sql = Path('city_guide/dev/sql/seed_poi_vilnius.sql').read_text()
#with engine.begin() as conn:
#    conn.execute(text(sql))
#PY

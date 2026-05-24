PYTHON ?= .venv/bin/python
UVICORN ?= .venv/bin/uvicorn
NPM ?= npm
BACKEND_SRC ?= backend/src

.PHONY: install install-api install-front api front check check-api check-front build openapi types

install: install-api install-front

install-api:
	python3 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

install-front:
	$(NPM) --prefix frontend ci

api:
	PYTHONPATH=$(BACKEND_SRC) $(UVICORN) open_data_hub.api:app --reload --host 127.0.0.1 --port 8000

front:
	$(NPM) --prefix frontend run dev -- --host 127.0.0.1 --port 5173

check: check-api check-front

check-api:
	$(PYTHON) -m mypy
	$(PYTHON) -m ruff check .

check-front:
	$(NPM) --prefix frontend run typecheck
	$(NPM) --prefix frontend run lint
	$(NPM) --prefix frontend run test:run

build:
	$(NPM) --prefix frontend run build

openapi:
	PYTHONPATH=$(BACKEND_SRC) $(PYTHON) backend/scripts/dump_openapi.py > frontend/openapi.json

types: openapi
	$(NPM) --prefix frontend run gen:types

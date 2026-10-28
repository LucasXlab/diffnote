PYTHON ?= python3
VENV ?= .venv
PY = $(VENV)/bin/python
.PHONY: dev lint format test build check demo wheel-smoke
dev:
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install 'setuptools==84.2.1' 'wheel==0.48.0'
	$(PY) -m pip install -e '.[dev]' --no-build-isolation
lint:
	$(PY) -m ruff check src tests scripts _build_backend.py
	$(PY) -m ruff format --check src tests scripts _build_backend.py
format:
	$(PY) -m ruff check --fix src tests scripts _build_backend.py
	$(PY) -m ruff format src tests scripts _build_backend.py
test:
	$(PY) -m pytest --cov=diffnote --cov-report=term-missing --cov-fail-under=70
build:
	$(PY) -m build --no-isolation
wheel-smoke: build
	$(PY) scripts/wheel_smoke.py
check: lint test wheel-smoke
demo:
	$(PY) scripts/demo.py

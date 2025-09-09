# Default Python; override via: `make PYTHON=python3.11 install`
PYTHON ?= python3.11

# Use uv to manage venv + lock
VENV := .venv

.PHONY: install lock sync lint fix type test clean

install:
	uv venv --python $(PYTHON)
	. $(VENV)/bin/activate && uv pip install -e ".[dev]"
	. $(VENV)/bin/activate && pre-commit install

lock:
	uv lock

sync:
	uv sync

lint:
	. $(VENV)/bin/activate && ruff check src tests
	. $(VENV)/bin/activate && black --check src tests

fix:
	. $(VENV)/bin/activate && ruff check --fix src tests
	. $(VENV)/bin/activate && black src tests

type:
	. $(VENV)/bin/activate && mypy src tests

test:
	. $(VENV)/bin/activate && pytest

clean:
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info


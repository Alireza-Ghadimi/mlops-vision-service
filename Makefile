# Default Python; override via: `make PYTHON=python3.11 install`
PYTHON ?= python3.11

# Use uv to manage venv + lock
VENV := .venv
IMAGE ?= mlops-vision-service:dev

.PHONY: lock install sync lint fix type test clean build-wheel docker-build docker-run docker-test

install:
	uv venv --python $(PYTHON)
	uv sync --frozenn ## Why??
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
	. $(VENV)/bin/activate && pytest -q

clean:
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info

build-wheel:
	. $(VENV)/bin/activate || true
	python -m pip install -U build
	pthon -m build --wheel
	@echo "Wheel(s) in ./dist:"
	@ls -1 dist/*.whl

docker-build:
	docker build -t $(IMAGE) .

docker-run:
	docker run --rm --user 10001:10001 $(IMAGE)

docker-test:
	docker run --rm --user 10001:10001 $(IMAGE) pytest -q

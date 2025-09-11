PYTHON ?= python3.11
VENV := .venv
P := $(VENV)/bin/python

.PHONY: lock install sync lint fix type test clean

lock:
	uv lock

install: lock
	uv venv --python $(PYTHON)
	$(P) -m pip install -U pip
	$(P) -m pip install -e ".[dev]"
	$(VENV)/bin/pre-commit install

lint:
	$(VENV)/bin/ruff check .
	$(VENV)/bin/black --check .

fix:
	$(VENV)/bin/ruff check --fix .
	$(VENV)/bin/black .

type:
	$(VENV)/bin/mypy src tests

test:
	$(VENV)/bin/pytest -q

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

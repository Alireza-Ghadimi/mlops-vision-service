PYTHON ?= python3.11
VENV := .venv
P := $(VENV)/bin/$(PYTHON)
IMAGE ?= mlops-vision-service:dev

.PHONY: lock install sync lint fix type test clean
remove:
	rm -rf $(VENV)
lock:
	uv lock

install: lock
	uv venv --python $(PYTHON)
	$(P) -m ensurepip --upgrade
	$(P) -m pip install -U pip
	$(P) -m pip install -e ".[dev]"
	$(VENV)/bin/pre-commit install

sync:
	uv venv --python $(PYTHON)
	uv lock
	uv sync --frozen --all-groups

py:
	$(P)


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
	$(P) -m pip install --upgrade pip
	$(P) -m pip install -U build
	$(P) -m build --wheel
	@echo "Wheel(s) in ./dist:"
	@ls -1 dist/*.whl

docker-build:
	docker build --no-cache -t $(IMAGE) .

docker-run:
	docker run --rm --user 10001:10001 $(IMAGE)

docker-test:
	docker run --rm --user 10001:10001 $(IMAGE) pytest -q
docker-shell:
	docker run --rm -it -p 8000:8000 --user 10001:10001 $(IMAGE) sh
api-run:
	$(VENV)/bin/uvicorn mlops_vision_service.api:app --host 0.0.0.0 --port 8000 --reload
check-api-health:
	curl -X GET http://localhost:8000/healthz | jq .
test-api-input:
	curl -X POST http://localhost:8000/predict \
	-F "image=@temp_c.jpg:type=image/jpeg" | jq .

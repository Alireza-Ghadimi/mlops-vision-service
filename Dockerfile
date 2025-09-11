# ---- Builder image ----------------------------------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Only copy what’s needed to build the wheel (faster cache)
COPY pyproject.toml README.md /app/
COPY src /app/src

RUN python -m pip install --upgrade pip build wheel \
 && python -m build --wheel --outdir /dist

# ---- Runtime image ----------------------------------------------------------
FROM python:3.11-slim AS runtime

# Create non-root user
RUN useradd -m -u 10001 appuser
WORKDIR /app

# Install just the built wheel (no dev deps)
COPY --from=builder /dist/*.whl /tmp/app.whl
RUN python -m pip install --no-cache-dir /tmp/app.whl \
 && rm -f /tmp/app.whl

USER appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Default: run our console script (prints a healthy startup message)
CMD ["mlops-vision-service"]

FROM python:3.11-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.7.1

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential libpq-dev curl git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml
COPY backend/ /app/backend/

WORKDIR /app
RUN pip install --upgrade pip setuptools wheel \
 && pip install -e ".[dev]" --no-cache-dir \
 && pip install 'uvicorn[standard]>=0.27.0' --no-cache-dir \
 && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')" 2>/dev/null || true \
 && python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')" 2>/dev/null || true

EXPOSE 8000

CMD ["python", "-m", "nyaya.cli", "run"]

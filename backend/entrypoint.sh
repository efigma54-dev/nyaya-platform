#!/bin/bash
set -e

echo "Running Alembic migrations..."
alembic upgrade head

echo "Seed already applied at build time, skipping..."

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

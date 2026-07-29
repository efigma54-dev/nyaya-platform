#!/bin/bash
# Quick start script for production verification
# Usage: bash backend/scripts/verification/quick_start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo "=========================================="
echo "Nyaya Platform Verification Quick Start"
echo "=========================================="
echo ""

# Check prerequisites
echo "[1/5] Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo "✗ Docker not found"
    exit 1
fi
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found"
    exit 1
fi
echo "✓ Prerequisites satisfied"
echo ""

# Install verification requirements
echo "[2/5] Installing verification dependencies..."
cd "$PROJECT_ROOT"
pip install -q requests psutil psycopg2-binary
echo "✓ Dependencies installed"
echo ""

# Start Docker services
echo "[3/5] Starting Docker services..."
docker compose up -d
sleep 10
docker compose ps
echo "✓ Services started"
echo ""

# Wait for services to be healthy
echo "[4/5] Waiting for services to become healthy..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker compose exec -T postgres pg_isready -U nyaya_user > /dev/null 2>&1; then
        echo "✓ PostgreSQL is ready"
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo "✗ Services did not become healthy in time"
    exit 1
fi
echo ""

# Run verification
echo "[5/5] Running production verification..."
cd "$PROJECT_ROOT"
python backend/scripts/verification/verify_all.py

VERIFICATION_RESULT=$?

# Print results
echo ""
echo "=========================================="
if [ $VERIFICATION_RESULT -eq 0 ]; then
    echo "✓ PRODUCTION VERIFICATION PASSED"
    echo "=========================================="
    echo "Platform is ready for production deployment."
    echo ""
    echo "Reports available in: evidence/runtime/"
    echo "Main report: evidence/runtime/production_acceptance.md"
else
    echo "✗ PRODUCTION VERIFICATION FAILED"
    echo "=========================================="
    echo "Please review the evidence reports for details."
    echo ""
    echo "Reports available in: evidence/runtime/"
fi
echo ""

exit $VERIFICATION_RESULT

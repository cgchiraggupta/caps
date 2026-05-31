#!/usr/bin/env bash
# HinglishCapsV3 start script
# Usage:
#   bash start.sh        # serve built frontend through FastAPI
#   bash start.sh --dev  # also start Vite dev server

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

export PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}"

PYTHON_BIN="${PYTHON_BIN:-python}"
API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"

echo "Starting HinglishCapsV3..."
echo "FastAPI app: http://${API_HOST}:${API_PORT}"
echo "API docs:    http://${API_HOST}:${API_PORT}/docs"

if [ "$1" = "--dev" ]; then
    echo "Starting Vite dev server on http://127.0.0.1:5173 ..."
    (cd frontend && npm run dev) &
    VITE_PID=$!
fi

"$PYTHON_BIN" -m uvicorn api.main:app --host "$API_HOST" --port "$API_PORT"

if [ -n "${VITE_PID:-}" ]; then
    kill "$VITE_PID" 2>/dev/null || true
fi

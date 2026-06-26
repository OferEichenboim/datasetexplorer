#!/bin/bash
PORT=${PORT:-8000}

# The --python sys.executable flag tells uv to use the active system Python
uv run --python sys.executable uvicorn main:app --host 0.0.0.0 --port "$PORT" --workers 4
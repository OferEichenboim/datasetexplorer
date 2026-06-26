#!/bin/bash
PORT=${PORT:-8000}

uv run --no-project uvicorn main:app --host 0.0.0.0 --port "$PORT" --workers 4
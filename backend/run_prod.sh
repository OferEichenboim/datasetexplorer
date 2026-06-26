#!/bin/bash
PORT=${PORT:-8000}

# Let uv run naturally using Render's native Python environment
uv run uvicorn main:app --host 0.0.0.0 --port "$PORT" --workers 4
#!/bin/bash
# Read Render's assigned port, or default to 8000 if running locally
PORT=${PORT:-8000}

uv run uvicorn main:app --host 0.0.0.0 --port "$PORT" --workers 4
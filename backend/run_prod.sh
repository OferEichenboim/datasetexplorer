#!/bin/bash
PORT=${PORT:-8000}

# Run the uvicorn binary directly from Render's virtual environment folder
./.venv/bin/uvicorn main:app --host 0.0.0.0 --port "$PORT" --workers 4
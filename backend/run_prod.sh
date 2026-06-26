#!/bin/bash
PORT=${PORT:-8000}

# Execute using the explicit virtual environment interpreter Render uses
/opt/render/project/src/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port "$PORT" --workers 4
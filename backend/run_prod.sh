#!/bin/bash
PORT=${PORT:-8000}

# Call uvicorn using the absolute system interpreter path Render just called out
/opt/render/project/src/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port "$PORT" --workers 4
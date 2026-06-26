#!/bin/bash
PORT=${PORT:-8000}

# Call uvicorn directly since Render already has it installed and active
uvicorn main:app --host 0.0.0.0 --port "$PORT" --workers 4
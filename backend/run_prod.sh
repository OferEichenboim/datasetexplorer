#!/bin/bash
PORT=${PORT:-8000}

# Execute uvicorn as a module using the active Python interpreter
python -m uvicorn main:app --host 0.0.0.0 --port "$PORT" --workers 4
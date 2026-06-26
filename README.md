# Dataset Explorer

Web app to upload a CSV, inspect rows, and ask natural-language questions that are translated to SQL and executed on SQLite.

## Tech Stack

- Backend: FastAPI + SQLite + OpenAI API
- Frontend: React + Vite + TypeScript

## Local Setup (Step by Step)

### 1) Prerequisites

- Python 3.14+
- Node.js 20+
- npm
- uv (Python package manager)

### 2) Configure backend environment

From the project root:

```bash
cp backend/.env.example backend/.env
```

Edit backend/.env and set at least:

- OPENAI_API_KEY: your OpenAI API key (required)
- OPENAI_MODEL: optional, default is gpt-4o-mini
- CORS_ALLOW_ORIGINS: optional comma-separated origins

### 3) Configure frontend environment

From the project root:

```bash
cp frontend/.env.example frontend/.env
```

Edit frontend/.env:

- VITE_API_BASE_URL: backend base URL (default local value is http://127.0.0.1:8000)

### 4) Install backend dependencies

```bash
cd backend
uv sync
```

### 5) Run backend

```bash
uv run uvicorn main:app --reload
```

Backend will run on http://127.0.0.1:8000

### 6) Install frontend dependencies

Open a second terminal:

```bash
cd frontend
npm install
```

### 7) Run frontend

```bash
npm run dev
```

Frontend will run on http://127.0.0.1:5173

## Runtime Configuration

### Environment variables

- backend/.env
  - OPENAI_API_KEY (required)
  - OPENAI_MODEL (optional)
  - CORS_ALLOW_ORIGINS (optional)
- frontend/.env
  - VITE_API_BASE_URL (optional if using local default)

### Backend static config

File: backend/cfg.json

- db_dir_path: directory for SQLite artifacts
- upload_dir_path: uploaded files directory
- db_path: SQLite database path
- openai_model: model fallback/default
- ask_max_rows: row limit for ask flow
- log_level: log level

## Main API Endpoints

- POST /upload-file: upload CSV and generate SQLite table
- GET /rows?page=1&page_size=50: paginated rows
- POST /ask: generate and run SQL from natural language

Example ask request:

```json
{
  "question": "What are the top 5 rows by revenue?",
  "dataset_id": "test_file.csv",
  "execute": true
}
```
 
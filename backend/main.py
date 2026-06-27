import os

from fastapi import FastAPI, status, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.db_generator.file_upload import FileUploadStrategyFactory
from services.db_generator.sqlite_generator import SQLiteTableGenerator
from exceptions.file_errors import FileServiceError
from exceptions.query_errors import QueryServiceError
from exceptions.rows_errors import RowsServiceError
from services.input_query.service import AskRequest
from services.rows.service import RowsService

app = FastAPI()

# ==========================
# CORS Configuration
# ==========================

def _normalize_origin(origin: str) -> str:
    return origin.strip().rstrip("/")


def _cors_origins() -> list[str]:
    configured = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
    defaults = {
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://datasetexplorer.vercel.app",
    }

    if configured:
        configured_origins = {
            _normalize_origin(origin)
            for origin in configured.split(",")
            if origin.strip()
        }
        defaults.update(configured_origins)

    return sorted(defaults)


def _cors_origin_regex() -> str:
    configured_regex = os.getenv("CORS_ALLOW_ORIGIN_REGEX", "").strip()
    if configured_regex:
        return configured_regex

    # Support this project's Vercel preview deployments.
    return r"https://datasetexplorer(?:-.*)?\.vercel\.app"


allowed_origins = _cors_origins()
allowed_origin_regex = _cors_origin_regex()
print(f"[CORS CONFIG] allow_origins={allowed_origins}")
print(f"[CORS CONFIG] allow_origin_regex={allowed_origin_regex}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allowed_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================
# API Endpoints
# ==========================

@app.get("/")
def read_root():
    return {"Hello": "Home page"}


@app.post("/upload-file")
def upload_file(file: UploadFile = File(...)):
    """
    Upload a file using the factory-provided strategy based on file type.
    """
    try:
        # 1. Trace incoming request
        print(f"[UPLOAD TRACE] Received file: {file.filename}")

        factory = FileUploadStrategyFactory.get_instance()
        strategy = factory.get_strategy(file.filename)
        print(f"[UPLOAD TRACE] Using strategy: {strategy.__class__.__name__}")

        # 2. Trace file writing stage
        saved_path = strategy.upload(file)
        print(f"[UPLOAD TRACE] File successfully written to disk at: {saved_path}")
        print(f"[UPLOAD TRACE] Does path exist? {os.path.exists(saved_path)}")

        # 3. Trace SQLite translation stage
        print("[UPLOAD TRACE] Starting SQLiteTableGenerator...")
        sqlite_generator = SQLiteTableGenerator()
        generation_result = sqlite_generator.generate_from_csv(saved_path)
        print(f"[UPLOAD TRACE] Generation complete! Result: {generation_result}")

        return {
            "status": "success",
            "path": str(saved_path),
            "message": "CSV uploaded and SQLite table generated successfully.",
            "sqlite": generation_result,
        }
    except FileServiceError as e:
        print(f"[UPLOAD ERROR] Caught expected FileServiceError: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        # 4. Catch ANY unhandled crash (e.g., FileNotFoundError, PermissionError)
        import traceback

        print(f"[UPLOAD CRITICAL FAILURE] Unhandled Exception: {str(e)}")
        print(traceback.format_exc())  # Prints the full stack trace to Render logs
        raise HTTPException(status_code=500, detail=f"Server-side failure: {str(e)}")


@app.post("/ask")
def ask_database(payload: AskRequest):
    """Accept free-text question, query LLM with context, return structured answer."""
    try:
        return AskRequest.handle_ask(
            question=payload.question,
            db_path="db/database.db",  # TODO: generalize this
        )
    except QueryServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@app.get("/rows")
def get_rows(page: int = 1, page_size: int = 50):
    """Return paginated rows from the current SQLite database table."""
    try:
        return RowsService().get_rows_page(page=page, page_size=page_size)
    except RowsServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

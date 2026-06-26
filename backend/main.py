from fastapi import FastAPI, status, File, UploadFile, HTTPException

from services.db_generator.file_upload import FileUploadStrategyFactory
from services.db_generator.sqlite_generator import SQLiteTableGenerator
from exceptions.file_errors import FileServiceError
from exceptions.query_errors import QueryServiceError
from exceptions.rows_errors import RowsServiceError
from services.input_query.service import AskRequest
from services.rows.service import RowsService

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "Home page"}

@app.post("/upload-file")
def upload_file(file: UploadFile = File(...)):
    """
    Upload a file using the factory-provided strategy based on file type.
    
    The factory automatically detects the file type and returns the appropriate
    strategy. Currently only CSV is supported, but adding new file types
    requires only registering a new strategy with the factory.
    """
    try:
        factory = FileUploadStrategyFactory.get_instance()
        strategy = factory.get_strategy(file.filename)
        saved_path = strategy.upload(file)
        sqlite_generator = SQLiteTableGenerator() #this should be separated from the upload functionality
        generation_result = sqlite_generator.generate_from_csv(saved_path)

        return {
            "status": "success",
            "path": saved_path,
            "message": "CSV uploaded and SQLite table generated successfully.",
            "sqlite": generation_result,
        }
    except FileServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@app.post("/ask")
def ask_database(payload: AskRequest):
    """Accept free-text question, query LLM with context, return structured answer."""
    try:
        return AskRequest.handle_ask(
            question=payload.question,
            db_path="db/database.db", #TODO: generalize this
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
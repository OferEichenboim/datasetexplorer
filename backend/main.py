from fastapi import FastAPI, Response, status, File, UploadFile
from pydantic import BaseModel

from services.db_generator.file_upload import FileUploadStrategyFactory
from exceptions.file_errors import FileServiceError

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "Home page"}

@app.post("/upload-csv")
def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file using the factory-provided strategy.
    
    The factory automatically detects the file type and returns the appropriate
    strategy. Currently only CSV is supported, but adding new file types
    requires only registering a new strategy with the factory.
    """
    try:
        factory = FileUploadStrategyFactory.get_instance()
        strategy = factory.get_strategy(file.filename)
        saved_path = strategy.upload(file)
        return {"status": "success", "path": saved_path}
    except FileServiceError as e:
        # Handle file service errors (unsupported type, validation errors, etc.)
        return {"status": "error", "message": str(e)}, status.HTTP_400_BAD_REQUEST

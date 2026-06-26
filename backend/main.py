from fastapi import FastAPI, Response, status, File, UploadFile
from pydantic import BaseModel

from services.db_generator.file_upload import FileUploadStrategyFactory


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
    factory = FileUploadStrategyFactory.get_instance()
    strategy = factory.get_strategy(file.filename)
    saved_path = strategy.upload(file)
    return {"status": "success", "path": saved_path}
    
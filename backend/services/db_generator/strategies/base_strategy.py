from pathlib import Path
from fastapi import UploadFile
from abc import ABC, abstractmethod


class FileUploadStrategy(ABC):
    """
    Abstract base class for file upload strategies.
    Each file type (CSV, JSON, Parquet, etc.) implements this interface.
    """

    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir
    
    @abstractmethod
    def clean_upload_dir(self):
        """
        Clean the upload directory by removing all existing files.
        """
        if self.upload_dir.exists() and self.upload_dir.is_dir():
            for existing_file in self.upload_dir.iterdir():
                if existing_file.is_file():
                    existing_file.unlink()

    @abstractmethod
    def upload(self, file: UploadFile) -> str:
        """
        Upload and save the file to disk.
        
        Args:
            file: UploadFile object from FastAPI
            
        Returns:
            str: Absolute path to the saved file
            
        Raises:
            Should raise custom exceptions from backend.exceptions.file_errors
        """
        pass
        
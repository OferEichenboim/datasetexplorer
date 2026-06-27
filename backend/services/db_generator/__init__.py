"""
File upload service module.

Provides factory-based file upload strategies for handling different file types.
Currently supports CSV files. New file types can be added by implementing
FileUploadStrategy and registering with FileUploadStrategyFactory.

Usage:
    from services.db_generator import FileUploadStrategyFactory
    
    factory = FileUploadStrategyFactory.get_instance()
    strategy = factory.get_strategy("data.csv")
    saved_path = strategy.upload(file)
"""

import os
from pathlib import Path

from .file_upload import (
    FileUploadStrategy,
    FileUploadStrategyFactory,
    CSVUploadStrategy,
)
from .sqlite_generator import SQLiteTableGenerator

__all__ = [
    "FileUploadStrategy",
    "FileUploadStrategyFactory",
    "CSVUploadStrategy",
    "SQLiteTableGenerator",
]

current_dir = Path(__file__).parent
db_path = current_dir.parent.parent / "db"
uploads_dir = current_dir.parent.parent / "uploaded_files"
os.makedirs(db_path, exist_ok=True)
os.makedirs(uploads_dir, exist_ok=True)

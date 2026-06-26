import json
import shutil
from pathlib import Path
from abc import ABC, abstractmethod
from fastapi import UploadFile
from typing import Dict, Type

# Load configuration
with open('cfg.json', 'r') as f:
    cfg = json.load(f)

upload_path = cfg.get('csv_dir_path', 'backend/db/uploaded_files/')


# ============================================================================
# ABSTRACT BASE CLASS & STRATEGY IMPLEMENTATIONS
# ============================================================================

class FileUploadStrategy(ABC):
    """
    Abstract base class for file upload strategies.
    Each file type (CSV, JSON, Parquet, etc.) implements this interface.
    """
    
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
        

class CSVUploadStrategy(FileUploadStrategy):
    """
    Strategy for uploading and saving CSV files.
    Validates file extension and streams to disk.
    """
    
    def upload(self, file: UploadFile) -> str:
        """
        Upload a CSV file with validation.
        
        Args:
            file: UploadFile object
            
        Returns:
            str: Absolute path to saved CSV file
            
        Raises:
            ValueError: If file extension is not .csv
        """
        # Validate file extension
        if not file.filename.endswith('.csv'):
            raise ValueError(f"File extension must be .csv, got {file.filename}")
        
        # Create upload directory if it doesn't exist
        upload_dir = Path(upload_path)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file to disk
        target_path = upload_dir / file.filename
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return str(target_path.resolve())


# ============================================================================
# FACTORY PATTERN
# ============================================================================

class FileUploadStrategyFactory:
    """
    Singleton factory that manages file upload strategies.
    
    Maintains a registry of strategies mapped by file extension.
    Provides a single point for creating and retrieving strategy instances.
    
    Usage:
        factory = FileUploadStrategyFactory.get_instance()
        strategy = factory.get_strategy("data.csv")
        saved_path = strategy.upload(file)
    """
    
    _instance = None
    
    def __init__(self):
        """Initialize the factory with an empty registry."""
        self._strategies: Dict[str, Type[FileUploadStrategy]] = {}
    
    @classmethod
    def get_instance(cls) -> "FileUploadStrategyFactory":
        """
        Get or create the singleton factory instance.
        
        Returns:
            FileUploadStrategyFactory: The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(self, file_extension: str, strategy_class: Type[FileUploadStrategy]) -> None:
        """
        Register a strategy for a given file extension.
        
        Args:
            file_extension: File extension (e.g., ".csv", ".json")
            strategy_class: Class inheriting from FileUploadStrategy
        """
        self._strategies[file_extension.lower()] = strategy_class
    
    def get_strategy(self, filename: str) -> FileUploadStrategy:
        """
        Get a strategy instance for the given filename.
        
        Determines file type from extension and returns appropriate strategy.
        
        Args:
            filename: Name of the file being uploaded
            
        Returns:
            FileUploadStrategy: Instantiated strategy ready for use
            
        Raises:
            UnsupportedFileTypeError: If file extension is not registered
        """
        from exceptions.file_errors import UnsupportedFileTypeError
        
        # Extract file extension
        file_extension = Path(filename).suffix.lower()
        
        # Look up strategy in registry
        strategy_class = self._strategies.get(file_extension)
        
        if strategy_class is None:
            raise UnsupportedFileTypeError(
                f"File type '{file_extension}' is not supported. "
                f"Supported types: {', '.join(self._strategies.keys())}"
            )
        
        # Return instantiated strategy
        return strategy_class()


# ============================================================================
# MODULE INITIALIZATION - Register strategies at import time
# ============================================================================

def _initialize_upload_strategies():
    """Register all available upload strategies with the factory."""
    factory = FileUploadStrategyFactory.get_instance()
    factory.register(".csv", CSVUploadStrategy)


# Initialize strategies when module is loaded
_initialize_upload_strategies()
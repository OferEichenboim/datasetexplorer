import json
from pathlib import Path
from typing import Dict, Type

from .strategies.base_strategy import FileUploadStrategy
from .strategies.csv_strategy import CSVUploadStrategy  

# ============================================================================
# CONFIGURATION & PATH RESOLUTION
# ============================================================================

# Resolve paths from the backend directory so cfg.json values stay portable.
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
CFG_PATH = BACKEND_ROOT / "cfg.json"

with CFG_PATH.open("r", encoding="utf-8") as f:
    cfg = json.load(f)

# cfg.json should store backend-relative paths like "db/uploaded_files".
UPLOAD_DIR_RELATIVE = Path(cfg.get("upload_dir_path", "db/uploaded_files"))
UPLOAD_DIR_ABSOLUTE = (BACKEND_ROOT / UPLOAD_DIR_RELATIVE).resolve()

class FileUploadStrategyFactory:

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
        
        # The factory injects shared dependencies so endpoint code stays stable.
        return strategy_class(UPLOAD_DIR_ABSOLUTE)


# ============================================================================
# MODULE INITIALIZATION - Register strategies at import time
# ============================================================================

def _initialize_upload_strategies():
    """Register all available upload strategies with the factory."""
    factory = FileUploadStrategyFactory.get_instance()
    factory.register(".csv", CSVUploadStrategy)


# Initialize strategies when module is loaded
_initialize_upload_strategies()
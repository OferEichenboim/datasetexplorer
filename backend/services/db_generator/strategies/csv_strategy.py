import shutil
from .base_strategy import FileUploadStrategy
from fastapi import UploadFile



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
        
        # Ensure upload directory exists (resolved by the factory)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file to disk
        target_path = self.upload_dir / file.filename
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return str(target_path.resolve())
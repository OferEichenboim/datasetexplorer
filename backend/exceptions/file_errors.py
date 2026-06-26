# backend/exceptions/file_errors.py

class FileServiceError(Exception):
    """
    Base exception for all errors that happen within the file service.
    Inheriting from this makes it easy to catch ALL file-related errors 
    at once if needed.
    """
    pass


class InvalidFileExtensionError(FileServiceError):
    """
    Raised when an uploaded file has an unsupported format or extension 
    (e.g., someone uploaded a .txt file instead of a .csv file).
    """
    pass


class EmptyFileError(FileServiceError):
    """
    Raised when the uploaded file contains 0 bytes of data.
    """
    pass


class StorageWriteError(FileServiceError):
    """
    Raised when the application fails to physically write the file to the 
    local disk or cloud storage (e.g., permission issues, disk full).
    """
    pass


class UnsupportedFileTypeError(FileServiceError):
    """
    Raised when a file type is not registered with the upload factory.
    This indicates the file extension is not supported by any available strategy.
    """
    pass


class DatabaseGenerationError(FileServiceError):
    """Raised when CSV-to-SQLite generation fails."""

    pass
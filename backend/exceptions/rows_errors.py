class RowsServiceError(Exception):
    """Base exception for rows retrieval failures."""


class InvalidPaginationError(RowsServiceError):
    """Raised when pagination parameters are invalid."""


class DatabaseReadError(RowsServiceError):
    """Raised when SQLite read operations fail."""

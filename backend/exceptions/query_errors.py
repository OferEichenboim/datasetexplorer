class QueryServiceError(Exception):
    """Base exception for query/LLM pipeline failures."""


class EmptyQuestionError(QueryServiceError):
    """Raised when the incoming ask question is empty."""


class DatasetResolutionError(QueryServiceError):
    """Raised when dataset selection fails or is ambiguous."""


class LLMServiceError(QueryServiceError):
    """Raised for OpenAI request/response failures."""


class UnsafeSQLRejectedError(QueryServiceError):
    """Raised when generated SQL violates safety policy."""
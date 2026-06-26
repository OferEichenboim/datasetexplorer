from dataclasses import dataclass
from math import ceil
from typing import Any

from exceptions.rows_errors import InvalidPaginationError


@dataclass(frozen=True)
class PaginationParams:
    page: int
    page_size: int

    @classmethod
    def build(cls, page: int, page_size: int, max_page_size: int) -> "PaginationParams":
        if page < 1:
            raise InvalidPaginationError("page must be greater than 0")
        if page_size < 1:
            raise InvalidPaginationError("page_size must be greater than 0")
        if page_size > max_page_size:
            raise InvalidPaginationError(
                f"page_size must be less than or equal to {max_page_size}"
            )
        return cls(page=page, page_size=page_size)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass(frozen=True)
class RowsPage:
    table_name: str
    page: int
    page_size: int
    total_rows: int
    rows: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        total_pages = ceil(self.total_rows / self.page_size) if self.total_rows else 0
        return {
            "table": self.table_name,
            "page": self.page,
            "page_size": self.page_size,
            "total_rows": self.total_rows,
            "total_pages": total_pages,
            "rows": self.rows,
        }

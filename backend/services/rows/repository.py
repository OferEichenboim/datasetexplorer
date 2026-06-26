import sqlite3
from pathlib import Path

from exceptions.rows_errors import DatabaseReadError
from services.rows.models import PaginationParams


class SQLiteRowsRepository:
    def __init__(self, db_path: Path):
        self._db_path = db_path

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        escaped = identifier.replace('"', '""')
        return f'"{escaped}"'

    def database_exists(self) -> bool:
        return self._db_path.exists()

    def get_first_table(self) -> str | None:
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                    LIMIT 1
                    """
                )
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error as exc:
            raise DatabaseReadError(f"Failed to inspect database tables: {exc}") from exc

    def count_rows(self, table_name: str) -> int:
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                quoted_table = self._quote_identifier(table_name)
                cursor.execute(f"SELECT COUNT(*) FROM {quoted_table}")
                row = cursor.fetchone()
                return int(row[0]) if row else 0
        except sqlite3.Error as exc:
            raise DatabaseReadError(f"Failed to count rows: {exc}") from exc

    def fetch_rows(self, table_name: str, pagination: PaginationParams) -> list[dict]:
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                quoted_table = self._quote_identifier(table_name)
                cursor.execute(
                    f"SELECT * FROM {quoted_table} LIMIT ? OFFSET ?",
                    (pagination.page_size, pagination.offset),
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            raise DatabaseReadError(f"Failed to fetch rows: {exc}") from exc

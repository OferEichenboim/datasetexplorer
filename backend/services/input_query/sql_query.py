import sqlite3
import pandas as pd

from exceptions.query_errors import QueryServiceError

class SQLQueryExecutor:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def run(self, query: str) -> list[dict]:
        """Execute a SQL query and return the results as a list of dictionaries."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # This allows us to fetch rows as dictionaries
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise QueryServiceError(f"Database error: {e}")
  
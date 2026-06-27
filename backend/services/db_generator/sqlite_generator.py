import csv
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from exceptions.file_errors import DatabaseGenerationError
from services.db_generator.file_upload import BACKEND_ROOT


CFG_PATH = BACKEND_ROOT / "cfg.json"


class SQLiteTableGenerator:
    """Build or refresh a SQLite table from an existing CSV file."""

    def __init__(self) -> None:
        with CFG_PATH.open("r", encoding="utf-8") as f:
            cfg = json.load(f)

        db_path_rel = Path(cfg.get("db_path", "db/database.db"))
        self.db_path = (BACKEND_ROOT / db_path_rel).resolve()

    @staticmethod
    def _sanitize_identifier(identifier: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9_]", "_", identifier.strip().lower())
        normalized = re.sub(r"_+", "_", normalized).strip("_")
        return normalized or "dataset"

    @staticmethod
    def _parse_int(value: str) -> int | None:
        if re.fullmatch(r"[+-]?\d+", value):
            return int(value)
        return None

    @staticmethod
    def _parse_float(value: str) -> float | None:
        # Accept decimal and exponent forms such as 12.3, .5, 1e6.
        if re.fullmatch(r"[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?", value):
            return float(value)
        return None

    @classmethod
    def _infer_column_types(cls, rows: list[dict[str, str]], columns: list[str]) -> dict[str, str]:
        inferred: dict[str, str] = {}
        for column in columns:
            saw_real = False
            saw_integer = False
            saw_text = False

            for row in rows:
                raw_value = (row.get(column, "") or "").strip()
                if raw_value == "":
                    continue

                int_value = cls._parse_int(raw_value)
                if int_value is not None:
                    saw_integer = True
                    continue

                float_value = cls._parse_float(raw_value)
                if float_value is not None:
                    saw_real = True
                    continue

                saw_text = True
                break

            if saw_text:
                inferred[column] = "TEXT"
            elif saw_real:
                inferred[column] = "REAL"
            elif saw_integer:
                inferred[column] = "INTEGER"
            else:
                inferred[column] = "TEXT"

        return inferred

    @classmethod
    def _convert_value(cls, value: str, sqlite_type: str) -> Any:
        raw_value = (value or "").strip()
        if raw_value == "":
            return None if sqlite_type in {"INTEGER", "REAL"} else ""

        if sqlite_type == "INTEGER":
            parsed_int = cls._parse_int(raw_value)
            return parsed_int if parsed_int is not None else raw_value

        if sqlite_type == "REAL":
            parsed_float = cls._parse_float(raw_value)
            return parsed_float if parsed_float is not None else raw_value

        return raw_value

    @staticmethod
    def _drop_existing_tables(conn: sqlite3.Connection) -> None:
        """Drop all user-created tables so each upload fully refreshes the DB."""
        existing_tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        for (table_name,) in existing_tables:
            conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')

    def generate(self, path: str) -> dict[str, str | int]:
        '''generate a SQLite table from a CSV file at the given path.
        TODO: refactor to support other file types in the future.'''
        
        file = Path(path).resolve()
        if not file.exists() or file.suffix.lower() != ".csv":
            raise DatabaseGenerationError("CSV source path is invalid or file is missing.")

        table_name = self._sanitize_identifier(file.stem)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with file.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                columns = reader.fieldnames or []
                if not columns:
                    raise DatabaseGenerationError("CSV file has no header row.")

                rows = list(reader)
                column_types = self._infer_column_types(rows, columns)

                with sqlite3.connect(self.db_path) as conn:
                    self._drop_existing_tables(conn)

                    quoted_cols = [f'"{col}" {column_types[col]}' for col in columns]
                    conn.execute(f'CREATE TABLE "{table_name}" ({", ".join(quoted_cols)})')

                    placeholders = ", ".join(["?"] * len(columns))
                    quoted_names = ", ".join([f'"{col}"' for col in columns])
                    insert_sql = (
                        f'INSERT INTO "{table_name}" ({quoted_names}) VALUES ({placeholders})'
                    )

                    row_count = 0
                    for row in rows:
                        converted_values = [
                            self._convert_value(row.get(col, ""), column_types[col]) for col in columns
                        ]
                        conn.execute(insert_sql, converted_values)
                        row_count += 1

                    conn.commit()

        except DatabaseGenerationError:
            raise
        except Exception as exc:
            raise DatabaseGenerationError(f"Failed to generate SQLite table: {exc}") from exc

        return {
            "db_path": str(self.db_path),
            "table_name": table_name,
            "row_count": row_count,
        }

import csv
import json
import re
import sqlite3
from pathlib import Path

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

    def generate_from_csv(self, csv_path: str) -> dict[str, str | int]:
        csv_file = Path(csv_path).resolve()
        if not csv_file.exists() or csv_file.suffix.lower() != ".csv":
            raise DatabaseGenerationError("CSV source path is invalid or file is missing.")

        table_name = self._sanitize_identifier(csv_file.stem)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with csv_file.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                columns = reader.fieldnames or []
                if not columns:
                    raise DatabaseGenerationError("CSV file has no header row.")

                with sqlite3.connect(self.db_path) as conn:
                    quoted_cols = [f'"{col}" TEXT' for col in columns]
                    conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')
                    conn.execute(f'CREATE TABLE "{table_name}" ({", ".join(quoted_cols)})')

                    placeholders = ", ".join(["?"] * len(columns))
                    quoted_names = ", ".join([f'"{col}"' for col in columns])
                    insert_sql = (
                        f'INSERT INTO "{table_name}" ({quoted_names}) VALUES ({placeholders})'
                    )

                    row_count = 0
                    for row in reader:
                        conn.execute(insert_sql, [row.get(col, "") for col in columns])
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

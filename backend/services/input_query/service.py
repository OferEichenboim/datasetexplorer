import os
import pandas as pd
from pathlib import Path
import sqlite3
from pydantic import BaseModel, Field
from openai import OpenAI

from exceptions.query_errors import DatasetResolutionError, EmptyQuestionError, LLMServiceError
from services.input_query.sql_query import SQLQueryExecutor


class SQLGeneration(BaseModel):
    sql_query: str = Field(description="The valid, raw SQLite query to execute. Do not include backticks.")
    explanation: str = Field(description="A brief description of what this query calculates.")


class AskRequest(BaseModel):
    '''Data model for the /ask endpoint request payload.
    The question is the user's free-text query, dataset_id is optional to specify a particular dataset, 
    and execute indicates whether to run the generated SQL query.
    '''
    
    question: str
    dataset_id: str | None = None
    execute: bool = True

    @staticmethod
    def _read_env_value(key: str) -> str:
        backend_root = Path(__file__).resolve().parents[2]
        for env_path in (backend_root / ".env", backend_root.parent / ".env"):
            if not env_path.exists():
                continue

            with env_path.open("r", encoding="utf-8") as env_file:
                for raw_line in env_file:
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue

                    current_key, value = line.split("=", 1)
                    if current_key.strip() == key:
                        return value.strip().strip('"').strip("'")

        return ""

    @staticmethod
    def _resolve_input_path(db_path: str) -> Path:
        path_obj = Path(db_path)
        if path_obj.is_absolute():
            resolved = path_obj
        else:
            backend_root = Path(__file__).resolve().parents[2]
            resolved = (backend_root / path_obj).resolve()

        if not resolved.exists():
            raise DatasetResolutionError(f"Input path was not found: {resolved}")

        return resolved

    @staticmethod
    def _csv_context(csv_path: Path, sample_rows: int = 5) -> str:
        df = pd.read_csv(csv_path, nrows=sample_rows)
        columns_info = ", ".join([f"{col} ({df[col].dtype})" for col in df.columns])
        csv_info = f"Source type: csv\nSource path: {csv_path.name}\nColumns: {columns_info}"
        return csv_info

    @staticmethod
    def _sqlite_context(sqlite_path: Path, sample_rows: int = 5) -> str:
        with sqlite3.connect(sqlite_path) as conn:
            tables_df = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name",
                conn,
            )

            if tables_df.empty:
                raise DatasetResolutionError("SQLite database has no user tables.")

            context_parts = [f"Source type: sqlite", f"Source path: {sqlite_path.name}"]

            for table_name in tables_df["name"].tolist()[:3]:
                schema_df = pd.read_sql_query(f'PRAGMA table_info("{table_name}")', conn)
                columns = schema_df["name"].tolist() if "name" in schema_df.columns else []
                sample_df = pd.read_sql_query(
                    f'SELECT * FROM "{table_name}" LIMIT {sample_rows}',
                    conn,
                )
                sample_json = sample_df.to_json(orient="records")
                context_parts.append(f"Table: {table_name}")
                context_parts.append(f"Columns: {', '.join(columns)}")
                context_parts.append(f"Sample rows: {sample_json}")

        return "\n".join(context_parts)


    @classmethod
    def _build_data_context(cls, db_path: str) -> str:
        resolved_path = cls._resolve_input_path(db_path)
        suffix = resolved_path.suffix.lower()

        if suffix == ".csv":
            return cls._csv_context(resolved_path)

        if suffix in {".db", ".sqlite", ".sqlite3"}:
            return cls._sqlite_context(resolved_path)

        
        raise DatasetResolutionError(
            f"Unsupported input format '{suffix}'. Use .csv or .db/.sqlite/.sqlite3"
        )

    @classmethod
    def handle_ask(cls, question: str, db_path: str) -> dict[str, str]:
        """Send the question and DB path to OpenAI and return the response text."""
        if not question or not question.strip():
            raise EmptyQuestionError("question must not be empty")

        resolved_db_path = cls._resolve_input_path(db_path)
        data_context = cls._build_data_context(db_path)

        api_key = os.getenv("OPENAI_API_KEY", "").strip() or cls._read_env_value("OPENAI_API_KEY")
        if not api_key:
            raise LLMServiceError("Missing OPENAI_API_KEY in backend/.env or project .env")

        try:
            client = OpenAI(api_key=api_key)
            completion = client.beta.chat.completions.parse(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                temperature=0,
                response_format=SQLGeneration,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise data assistant translation layer. "
                            "Your job is to translate the user's question into a single valid SQLite query. "
                            "Base your query strictly on the provided table schema context."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Question: {question}\n\nSchema Context:\n{data_context}",
                    },
                ],
            )
        except Exception as exc:
            raise LLMServiceError(f"Failed to query OpenAI: {exc}") from exc

        # Extract parsed structural payload safely
        parsed_response = completion.choices[0].message.parsed
        if not parsed_response:
            raise LLMServiceError("LLM structured output parsing failed; got None.")

        generated_sql = parsed_response.sql_query
        explanation = parsed_response.explanation

        records = SQLQueryExecutor(db_path).run(generated_sql)  # Validate SQL execution without returning data


        # Return the clean, structured package directly back to your FastAPI route response
        return {
            "status": "success",
            "question": question,
            "generated_sql": generated_sql,
            "explanation": explanation,
            "data": records  # This goes directly into your React data table view!
        }
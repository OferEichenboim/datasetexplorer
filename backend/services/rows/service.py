import json
from pathlib import Path

from services.rows.models import PaginationParams, RowsPage
from services.rows.repository import SQLiteRowsRepository


class DBPathResolver:
    def __init__(self, backend_root: Path):
        self._backend_root = backend_root
        self._cfg_path = backend_root / "cfg.json"

    def resolve(self) -> Path:
        if not self._cfg_path.exists():
            return (self._backend_root / "db/database.db").resolve()

        with self._cfg_path.open("r", encoding="utf-8") as cfg_file:
            cfg = json.load(cfg_file)

        db_path_rel = Path(cfg.get("db_path", "db/database.db"))
        return (self._backend_root / db_path_rel).resolve()

    def max_page_size(self) -> int:
        if not self._cfg_path.exists():
            return 200

        with self._cfg_path.open("r", encoding="utf-8") as cfg_file:
            cfg = json.load(cfg_file)

        cfg_value = cfg.get("ask_max_rows", 200)
        return int(cfg_value) if int(cfg_value) > 0 else 200


class RowsService:
    def __init__(self) -> None:
        backend_root = Path(__file__).resolve().parents[2]
        self._db_path_resolver = DBPathResolver(backend_root=backend_root)

    def get_rows_page(self, page: int = 1, page_size: int = 50) -> dict | None:
        pagination = PaginationParams.build(
            page=page,
            page_size=page_size,
            max_page_size=self._db_path_resolver.max_page_size(),
        )

        repository = SQLiteRowsRepository(self._db_path_resolver.resolve())
        if not repository.database_exists():
            return None

        table_name = repository.get_first_table()
        if not table_name:
            return None

        total_rows = repository.count_rows(table_name)
        rows = repository.fetch_rows(table_name, pagination)

        return RowsPage(
            table_name=table_name,
            page=pagination.page,
            page_size=pagination.page_size,
            total_rows=total_rows,
            rows=rows,
        ).to_dict()

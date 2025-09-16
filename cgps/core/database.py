import sqlite3
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Optional


class Database:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._conn = None

    def connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(
                self._db_path,
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
    
    def begin(self) -> None:
        self.connection().execute("BEGIN")

    def commit(self) -> None:
        self.connection().commit()

    def execute(self, sql: str, params: Mapping[str, Any]) -> int:
        cur = self.connection().execute(sql, params)
        rc = cur.lastrowid
        cur.close()
        return rc

    def fetchone(
        self, sql: str, params: Iterable[Any] = ()
    ) -> Optional[dict[str, Any]]:
        cur = self.connection().execute(sql, tuple(params))
        row = cur.fetchone()
        cur.close()
        return dict(row) if row is not None else None

    def fetchall(self, sql: str, params: Iterable[Any] = ()) -> List[dict[str, any]]:
        cur = self.connection().execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
        cur.close()
        return rows

    def migrate_from_file(self, path: Path) -> None:
        sql_text = path.read_text(encoding="utf-8")
        self.connection().executescript(sql_text)

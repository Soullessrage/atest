from __future__ import annotations

import json
from sqlite3 import Connection
from typing import Iterable, Type

from app.data.repositories.base import Repository


class SqliteRepository(Repository):
    def __init__(self, conn: Connection, table_name: str, model_cls: Type, table_fields: Iterable[str], json_fields: Iterable[str] = ()):  # type: ignore[override]
        self.conn = conn
        self.table_name = table_name
        self.model_cls = model_cls
        self.table_fields = list(table_fields)
        self.json_fields = set(json_fields)

    def _prepare_record(self, item: object) -> dict[str, object]:
        def normalize(value: object) -> object:
            if isinstance(value, bool):
                return int(value)
            if hasattr(value, "isoformat") and not isinstance(value, str):
                try:
                    return value.isoformat()  # type: ignore[arg-type]
                except Exception:
                    pass
            return value

        record = {field: normalize(getattr(item, field)) for field in self.table_fields}
        for json_field in self.json_fields:
            record[json_field] = json.dumps(record.get(json_field, {}), default=str)
        return record

    def _record_to_instance(self, row: dict[str, object]) -> object:
        payload = {key: row[key] for key in row.keys()}
        for json_field in self.json_fields:
            payload[json_field] = json.loads(payload.get(json_field) or "null")
        if hasattr(self.model_cls, "from_dict"):
            return self.model_cls.from_dict(payload)
        return self.model_cls(**payload)

    def add(self, item: object) -> None:
        record = self._prepare_record(item)
        columns = ", ".join(record.keys())
        placeholders = ", ".join("?" for _ in record)
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        self.conn.execute(sql, tuple(record.values()))
        self.conn.commit()

    def add_or_update(self, item: object) -> None:
        if self.get(item.id) is None:
            self.add(item)
        else:
            self.update(item)

    def get(self, item_id: str):
        row = self.conn.execute(
            f"SELECT * FROM {self.table_name} WHERE id = ?", (item_id,)
        ).fetchone()
        return self._record_to_instance(dict(row)) if row else None

    def list(self) -> list[object]:
        rows = self.conn.execute(f"SELECT * FROM {self.table_name}").fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]

    def update(self, item: object) -> None:
        record = self._prepare_record(item)
        assignments = ", ".join(f"{key} = ?" for key in record if key != "id")
        sql = f"UPDATE {self.table_name} SET {assignments} WHERE id = ?"
        values = tuple(record[key] for key in record if key != "id") + (record["id"],)
        self.conn.execute(sql, values)
        self.conn.commit()

    def remove(self, item_id: str) -> None:
        self.conn.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (item_id,))
        self.conn.commit()

from __future__ import annotations

from app.data.repositories.sqlite_repository import SqliteRepository
from app.domain.models.structure import Empire


class EmpireRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "world_id",
            "continent_id",
            "name",
            "description",
            "ruler_name",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        super().__init__(conn, "empires", Empire, table_fields, json_fields=("metadata",))

    def list_by_world(self, world_id: str) -> list[Empire]:
        rows = self.conn.execute("SELECT * FROM empires WHERE world_id = ?", (world_id,)).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]

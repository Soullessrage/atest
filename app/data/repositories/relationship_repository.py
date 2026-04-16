from __future__ import annotations

from app.data.repositories.sqlite_repository import SqliteRepository
from app.domain.models.relationship import Relationship


class RelationshipRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "world_id",
            "source_id",
            "target_id",
            "relation_type",
            "weight",
            "history",
            "tags",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        json_fields = ("history", "tags", "metadata")
        super().__init__(conn, "relationships", Relationship, table_fields, json_fields=json_fields)

    def list_by_world(self, world_id: str) -> list[Relationship]:
        rows = self.conn.execute("SELECT * FROM relationships WHERE world_id = ?", (world_id,)).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]

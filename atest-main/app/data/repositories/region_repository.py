from __future__ import annotations

from app.data.repositories.sqlite_repository import SqliteRepository
from app.domain.models.structure import Region


class RegionRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "world_id",
            "continent_id",
            "empire_id",
            "kingdom_id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
            "settlement_ids",
            "point_of_interest_ids",
        )
        super().__init__(conn, "regions", Region, table_fields, json_fields=("metadata", "settlement_ids", "point_of_interest_ids"))

    def list_by_world(self, world_id: str) -> list[Region]:
        rows = self.conn.execute("SELECT * FROM regions WHERE world_id = ?", (world_id,)).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]

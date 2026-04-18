from __future__ import annotations

from app.data.repositories.sqlite_repository import SqliteRepository
from app.domain.models.structure import SettlementNode


class SettlementRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "world_id",
            "continent_id",
            "empire_id",
            "kingdom_id",
            "region_id",
            "name",
            "description",
            "settlement_type",
            "population",
            "location",
            "housing_summary",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
            "connected_routes",
            "tags",
        )
        super().__init__(conn, "settlement_nodes", SettlementNode, table_fields, json_fields=("location", "housing_summary", "metadata", "connected_routes", "tags"))

    def list_by_world(self, world_id: str) -> list[SettlementNode]:
        rows = self.conn.execute("SELECT * FROM settlement_nodes WHERE world_id = ?", (world_id,)).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]

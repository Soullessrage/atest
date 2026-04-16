from __future__ import annotations

from app.data.repositories.sqlite_repository import SqliteRepository
from app.domain.models.structure import Route


class RouteRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "source_id",
            "target_id",
            "distance",
            "route_type",
            "notes",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        json_fields = ("metadata",)
        super().__init__(conn, "routes", Route, table_fields, json_fields=json_fields)

    def list_by_world(self, world_id: str) -> list[Route]:
        rows = self.conn.execute(
            "SELECT r.* FROM routes r JOIN settlement_nodes s ON r.source_id = s.id WHERE s.world_id = ?",
            (world_id,),
        ).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]

from __future__ import annotations

from app.data.repositories.sqlite_repository import SqliteRepository
from app.domain.models.structure import World


class WorldRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        super().__init__(conn, "worlds", World, table_fields, json_fields=("metadata",))

"""Repository for Race entities."""

from __future__ import annotations

from app.data.repositories.sqlite_repository import SqliteRepository
from app.domain.models.race import Race


class RaceRepository(SqliteRepository):
    """Repository for managing Race entities in SQLite."""

    def __init__(self, conn):
        table_fields = (
            "id",
            "name",
            "description",
            "cultural_tags",
            "lifespan",
            "preferred_occupations",
            "settlement_preferences",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        json_fields = ("cultural_tags", "preferred_occupations", "settlement_preferences", "metadata")
        super().__init__(conn, "races", Race, table_fields, json_fields=json_fields)

from __future__ import annotations

from app.data.repositories.sqlite_repository import SqliteRepository
from app.domain.events.event import EventDefinition, EventInstance


class EventDefinitionRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "world_id",
            "name",
            "description",
            "scope",
            "category",
            "probability",
            "duration_days",
            "conditions",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        json_fields = ("conditions", "metadata")
        super().__init__(conn, "event_definitions", EventDefinition, table_fields, json_fields=json_fields)

    def list_by_world(self, world_id: str) -> list[EventDefinition]:
        rows = self.conn.execute("SELECT * FROM event_definitions WHERE world_id = ?", (world_id,)).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]


class EventInstanceRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "definition_id",
            "world_id",
            "occurred_at",
            "affected_scope",
            "effect_summary",
            "details",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        json_fields = ("details", "metadata")
        super().__init__(conn, "event_instances", EventInstance, table_fields, json_fields=json_fields)

    def list_by_world(self, world_id: str) -> list[EventInstance]:
        rows = self.conn.execute("SELECT * FROM event_instances WHERE world_id = ?", (world_id,)).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]

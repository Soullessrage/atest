from __future__ import annotations

from app.data.repositories.sqlite_repository import SqliteRepository
from app.domain.models.npc import NPC


class NPCRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "world_id",
            "settlement_id",
            "name",
            "description",
            "age",
            "gender",
            "race_id",
            "subrace_id",
            "occupation",
            "social_role",
            "residence_id",
            "wealth_status",
            "personality_traits",
            "goals",
            "motivations",
            "flaws",
            "history",
            "family_ids",
            "relationship_ids",
            "tags",
            "health_status",
            "injuries",
            "illnesses",
            "fertility_score",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        json_fields = (
            "personality_traits",
            "goals",
            "motivations",
            "flaws",
            "history",
            "family_ids",
            "relationship_ids",
            "tags",
            "injuries",
            "illnesses",
            "metadata",
        )
        super().__init__(conn, "npcs", NPC, table_fields, json_fields=json_fields)

    def list_by_world(self, world_id: str) -> list[NPC]:
        rows = self.conn.execute("SELECT * FROM npcs WHERE world_id = ?", (world_id,)).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]

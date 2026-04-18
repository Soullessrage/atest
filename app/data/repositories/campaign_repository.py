from __future__ import annotations

from app.data.repositories.sqlite_repository import SqliteRepository
from app.domain.models.campaign import (
    Campaign,
    Party,
    Character,
    Encounter,
    Quest,
    JournalEntry,
)


class CampaignRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "world_id",
            "name",
            "description",
            "game_master_name",
            "current_date",
            "session_count",
            "notes",
            "party_id",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        super().__init__(
            conn,
            "campaigns",
            Campaign,
            table_fields,
            json_fields=("metadata",),
        )

    def list_by_world(self, world_id: str) -> list[Campaign]:
        rows = self.conn.execute(
            "SELECT * FROM campaigns WHERE world_id = ?", (world_id,)
        ).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]

    def list_active(self) -> list[Campaign]:
        rows = self.conn.execute("SELECT * FROM campaigns WHERE 1=1").fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]


class PartyRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "campaign_id",
            "world_id",
            "name",
            "description",
            "current_settlement_id",
            "character_ids",
            "party_gold",
            "party_inventory",
            "founded_date",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        super().__init__(
            conn,
            "parties",
            Party,
            table_fields,
            json_fields=("character_ids", "party_inventory", "metadata"),
        )

    def list_by_campaign(self, campaign_id: str) -> list[Party]:
        rows = self.conn.execute(
            "SELECT * FROM parties WHERE campaign_id = ?", (campaign_id,)
        ).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]


class CharacterRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "campaign_id",
            "party_id",
            "player_name",
            "name",
            "description",
            "character_class",
            "race",
            "background",
            "level",
            "experience",
            "hit_points",
            "max_hit_points",
            "armor_class",
            "alignment",
            "personality_traits",
            "ideals",
            "bonds",
            "flaws",
            "ability_scores",
            "skills",
            "proficiencies",
            "equipment",
            "spells",
            "feats",
            "backstory",
            "current_location",
            "gold",
            "status",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        super().__init__(
            conn,
            "characters",
            Character,
            table_fields,
            json_fields=("ability_scores", "skills", "proficiencies", "equipment", "spells", "feats", "metadata"),
        )

    def list_by_party(self, party_id: str) -> list[Character]:
        rows = self.conn.execute(
            "SELECT * FROM characters WHERE party_id = ?", (party_id,)
        ).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]


class EncounterRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "campaign_id",
            "world_id",
            "party_id",
            "encounter_type",
            "location",
            "difficulty",
            "enemies",
            "objectives",
            "reward_xp",
            "reward_gold",
            "completed",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        super().__init__(
            conn,
            "encounters",
            Encounter,
            table_fields,
            json_fields=("enemies", "objectives", "metadata"),
        )

    def list_by_campaign(self, campaign_id: str) -> list[Encounter]:
        rows = self.conn.execute(
            "SELECT * FROM encounters WHERE campaign_id = ?", (campaign_id,)
        ).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]


class QuestRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "campaign_id",
            "party_id",
            "giver_npc_id",
            "title",
            "description",
            "objectives",
            "reward_xp",
            "reward_gold",
            "reward_items",
            "status",
            "difficulty",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        super().__init__(
            conn,
            "quests",
            Quest,
            table_fields,
            json_fields=("objectives", "reward_items", "metadata"),
        )

    def list_by_campaign(self, campaign_id: str) -> list[Quest]:
        rows = self.conn.execute(
            "SELECT * FROM quests WHERE campaign_id = ?", (campaign_id,)
        ).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]

    def list_active(self) -> list[Quest]:
        rows = self.conn.execute(
            "SELECT * FROM quests WHERE status IN ('available', 'active')"
        ).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]


class JournalEntryRepository(SqliteRepository):
    def __init__(self, conn):
        table_fields = (
            "id",
            "campaign_id",
            "session_date",
            "session_number",
            "content",
            "party_location",
            "events",
            "notes",
            "created_at",
            "updated_at",
            "locked",
            "metadata",
        )
        super().__init__(
            conn,
            "journal_entries",
            JournalEntry,
            table_fields,
            json_fields=("events", "metadata"),
        )

    def list_by_campaign(self, campaign_id: str) -> list[JournalEntry]:
        rows = self.conn.execute(
            "SELECT * FROM journal_entries WHERE campaign_id = ? ORDER BY session_number DESC",
            (campaign_id,),
        ).fetchall()
        return [self._record_to_instance(dict(row)) for row in rows]


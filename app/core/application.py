from __future__ import annotations

from pathlib import Path

from app.core.services.import_export_service import ImportExportService
from app.core.services.persistence_service import PersistenceService
from app.core.services.simulation_service import SimulationService
from app.core.services.campaign_service import CampaignService
from app.data.repositories.campaign_repository import (
    CampaignRepository,
    PartyRepository,
    CharacterRepository,
    EncounterRepository,
    QuestRepository,
    JournalEntryRepository,
)
from app.data.snapshots.manager import SnapshotManager
from app.data.sqlite.database import initialize_database


class ApplicationContext:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.database_path = data_path / "world_sim.db"
        self.db = initialize_database(self.database_path)
        self.persistence_service = PersistenceService(self.db)
        self.import_export_service = ImportExportService(self.db)
        self.simulation_service = SimulationService(self.db)
        self.campaign_repository = CampaignRepository(self.db)
        self.party_repository = PartyRepository(self.db)
        self.character_repository = CharacterRepository(self.db)
        self.encounter_repository = EncounterRepository(self.db)
        self.quest_repository = QuestRepository(self.db)
        self.journal_entry_repository = JournalEntryRepository(self.db)
        self.campaign_service = CampaignService(
            campaign_repo=self.campaign_repository,
            party_repo=self.party_repository,
            character_repo=self.character_repository,
            encounter_repo=self.encounter_repository,
            quest_repo=self.quest_repository,
            journal_entry_repo=self.journal_entry_repository,
            persistence_service=self.persistence_service,
        )
        self.snapshot_manager = SnapshotManager(
            self.data_path / "snapshots",
            persistence_service=self.persistence_service,
            import_export_service=self.import_export_service,
        )

    def close(self) -> None:
        self.db.close()

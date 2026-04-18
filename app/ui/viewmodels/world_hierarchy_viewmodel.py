from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from app.core.services.import_export_service import ImportExportService
from app.core.services.persistence_service import PersistenceService
from app.domain.models.structure import Continent, Empire, Kingdom, Region, SettlementNode, World


class WorldHierarchyViewModel:
    def __init__(
        self,
        persistence_service: PersistenceService,
        import_export_service: ImportExportService,
    ):
        self.persistence_service = persistence_service
        self.import_export_service = import_export_service

    def list_worlds(self) -> List[World]:
        return self.persistence_service.list_worlds()

    def load_world_details(self, world_id: str) -> Dict[str, object]:
        world = self.persistence_service.load_world(world_id)
        if world is None:
            raise ValueError(f"World {world_id} not found")
        return {
            "world": world,
            "continents": self.persistence_service.list_continents(world_id),
            "empires": self.persistence_service.list_empires(world_id),
            "kingdoms": self.persistence_service.list_kingdoms(world_id),
            "regions": self.persistence_service.list_regions(world_id),
            "settlements": self.persistence_service.list_settlements(world_id),
        }

    def export_world(self, world_id: str, path: Path) -> None:
        world = self.persistence_service.load_world(world_id)
        if world is None:
            raise ValueError(f"World {world_id} not found")
        self.import_export_service.export_full_world(world.id, path)

    def import_world(self, path: Path) -> World:
        return self.import_export_service.import_world(path)

    def get_world_by_id(self, world_id: str) -> Optional[World]:
        return self.persistence_service.load_world(world_id)

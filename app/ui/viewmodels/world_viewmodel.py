from __future__ import annotations

from pathlib import Path
from typing import List

from app.core.services.persistence_service import PersistenceService
from app.core.services.import_export_service import ImportExportService
from app.domain.models.structure import World


class WorldOverviewViewModel:
    def __init__(self, persistence_service: PersistenceService, import_export_service: ImportExportService):
        self.persistence_service = persistence_service
        self.import_export_service = import_export_service

    def list_worlds(self) -> List[World]:
        return self.persistence_service.list_worlds()

    def create_world(self, name: str, description: str = "") -> World:
        world = World(name=name, description=description)
        self.persistence_service.create_world(world)
        return world

    def export_world(self, world: World, path: Path) -> None:
        self.import_export_service.export_world(world, path)

from __future__ import annotations

from pathlib import Path
from sqlite3 import Connection

from app.data.jsonio.exporter import JsonExporter
from app.data.jsonio.importer import JsonImporter
from app.data.repositories import (
    ContinentRepository,
    EmpireRepository,
    EventDefinitionRepository,
    EventInstanceRepository,
    KingdomRepository,
    NPCRepository,
    RelationshipRepository,
    RegionRepository,
    RouteRepository,
    SettlementRepository,
    WorldRepository,
)
from app.domain.models import World


class ImportExportService:
    def __init__(self, conn: Connection):
        self.world_repository = WorldRepository(conn)
        self.continent_repository = ContinentRepository(conn)
        self.empire_repository = EmpireRepository(conn)
        self.kingdom_repository = KingdomRepository(conn)
        self.region_repository = RegionRepository(conn)
        self.settlement_repository = SettlementRepository(conn)
        self.npc_repository = NPCRepository(conn)
        self.relationship_repository = RelationshipRepository(conn)
        self.route_repository = RouteRepository(conn)
        self.event_definition_repository = EventDefinitionRepository(conn)
        self.event_instance_repository = EventInstanceRepository(conn)
        self.exporter = JsonExporter()
        self.importer = JsonImporter(
            world_repository=self.world_repository,
            continent_repository=self.continent_repository,
            empire_repository=self.empire_repository,
            kingdom_repository=self.kingdom_repository,
            region_repository=self.region_repository,
            settlement_repository=self.settlement_repository,
            npc_repository=self.npc_repository,
            relationship_repository=self.relationship_repository,
            route_repository=self.route_repository,
            event_definition_repository=self.event_definition_repository,
            event_instance_repository=self.event_instance_repository,
        )

    def export_world(self, world: World, path: Path) -> None:
        package = self.exporter.export_world(world)
        package.to_json(path)

    def export_full_world(self, world_id: str, path: Path) -> None:
        world = self.world_repository.get(world_id)
        if world is None:
            raise ValueError(f"World {world_id} not found")

        package = self.exporter.export_full_world(
            world=world,
            continents=self.continent_repository.list_by_world(world_id),
            empires=self.empire_repository.list_by_world(world_id),
            kingdoms=self.kingdom_repository.list_by_world(world_id),
            regions=self.region_repository.list_by_world(world_id),
            settlements=self.settlement_repository.list_by_world(world_id),
            npcs=self.npc_repository.list_by_world(world_id),
            relationships=self.relationship_repository.list_by_world(world_id),
            routes=self.route_repository.list_by_world(world_id),
            event_definitions=self.event_definition_repository.list_by_world(world_id),
            event_instances=self.event_instance_repository.list_by_world(world_id),
        )
        package.to_json(path)

    def import_world(self, path: Path, overwrite: bool = False) -> World:
        package = self.importer.from_file(path)
        return self.importer.import_package(package, overwrite=overwrite)

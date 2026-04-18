from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from app.core.services.persistence_service import PersistenceService
from app.core.services.import_export_service import ImportExportService
from app.domain.models.structure import (
    Continent,
    Empire,
    Kingdom,
    Region,
    SettlementNode,
    SettlementType,
    World,
)


class WorldOverviewViewModel:
    def __init__(self, persistence_service: PersistenceService, import_export_service: ImportExportService):
        self.persistence_service = persistence_service
        self.import_export_service = import_export_service

    def list_worlds(self) -> List[World]:
        return self.persistence_service.list_worlds()

    def list_worlds_with_counts(self) -> List[Dict]:
        worlds = self.persistence_service.list_worlds()
        result = []
        for world in worlds:
            settlement_count = len(self.persistence_service.list_settlements(world.id))
            kingdom_count = len(self.persistence_service.list_kingdoms(world.id))
            empire_count = len(self.persistence_service.list_empires(world.id))
            result.append({
                "world": world,
                "settlement_count": settlement_count,
                "kingdom_count": kingdom_count,
                "empire_count": empire_count,
            })
        return result

    def get_world_by_id(self, world_id: str) -> Optional[World]:
        return self.persistence_service.load_world(world_id)

    def create_world(self, name: str, description: str = "") -> World:
        world = World(name=name, description=description)
        self.persistence_service.create_world(world)
        return world

    def create_sample_world(self, name: str = "Erdania", description: str = "A fresh sample world with hierarchical structure.") -> World:
        world = World(name=name, description=description)
        self.persistence_service.create_world(world)

        continent = Continent(
            world_id=world.id,
            name="Aurora",
            description="A sweeping continent of magic and kingdoms.",
        )
        self.persistence_service.create_continent(continent)

        empire = Empire(
            world_id=world.id,
            continent_id=continent.id,
            name="Solaris Empire",
            ruler_name="Empress Valeria",
            description="A shining empire that spans the eastern coast.",
        )
        self.persistence_service.create_empire(empire)

        kingdom = Kingdom(
            world_id=world.id,
            continent_id=continent.id,
            empire_id=empire.id,
            name="Kingdom of Emberfall",
            description="A vibrant kingdom built around a grand river.",
        )
        self.persistence_service.create_kingdom(kingdom)

        region = Region(
            world_id=world.id,
            continent_id=continent.id,
            empire_id=empire.id,
            kingdom_id=kingdom.id,
            name="Ember Plains",
            description="Rolling plains surrounding the capital.",
        )
        self.persistence_service.create_region(region)

        settlement = SettlementNode(
            world_id=world.id,
            continent_id=continent.id,
            empire_id=empire.id,
            kingdom_id=kingdom.id,
            region_id=region.id,
            name="Emberfall City",
            description="The capital city of the Emberfall kingdom.",
            settlement_type=SettlementType.CITY.value,
            population=24000,
            location={"x": 420.0, "y": 210.0},
            connected_routes=[],
            housing_summary={"homes": 5800},
        )
        self.persistence_service.create_settlement(settlement)

        continent.empire_ids = [empire.id]
        continent.kingdom_ids = [kingdom.id]
        continent.region_ids = [region.id]
        continent.settlement_ids = [settlement.id]
        self.persistence_service.update_continent(continent)

        empire.kingdom_ids = [kingdom.id]
        self.persistence_service.update_empire(empire)

        kingdom.region_ids = [region.id]
        kingdom.capital_settlement_id = settlement.id
        self.persistence_service.update_kingdom(kingdom)

        region.settlement_ids = [settlement.id]
        self.persistence_service.update_region(region)

        world.continents = [continent.id]
        world.empires = [empire.id]
        world.kingdoms = [kingdom.id]
        world.regions = [region.id]
        world.settlements = [settlement.id]
        self.persistence_service.update_world(world)

        return world

    def load_world_details(self, world_id: str) -> Dict[str, object]:
        return {
            "world": self.persistence_service.load_world(world_id),
            "continents": self.persistence_service.list_continents(world_id),
            "empires": self.persistence_service.list_empires(world_id),
            "kingdoms": self.persistence_service.list_kingdoms(world_id),
            "regions": self.persistence_service.list_regions(world_id),
            "settlements": self.persistence_service.list_settlements(world_id),
        }

    def export_world(self, world: World, path: Path) -> None:
        self.import_export_service.export_world(world, path)

    def export_full_world(self, world: World, path: Path) -> None:
        self.import_export_service.export_full_world(world.id, path)

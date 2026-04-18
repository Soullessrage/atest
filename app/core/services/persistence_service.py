from __future__ import annotations

from typing import Optional
from sqlite3 import Connection

from app.data.repositories import (
    ContinentRepository,
    EmpireRepository,
    EventDefinitionRepository,
    EventInstanceRepository,
    KingdomRepository,
    NPCRepository,
    RaceRepository,
    RelationshipRepository,
    RegionRepository,
    RouteRepository,
    SettlementRepository,
    WorldRepository,
)
from app.domain.events.event import EventDefinition, EventInstance
from app.domain.models import (
    Continent,
    Empire,
    Kingdom,
    NPC,
    Relationship,
    Region,
    Route,
    SettlementNode,
    World,
)


class PersistenceService:
    def __init__(self, conn: Connection):
        self.world_repository = WorldRepository(conn)
        self.continent_repository = ContinentRepository(conn)
        self.empire_repository = EmpireRepository(conn)
        self.kingdom_repository = KingdomRepository(conn)
        self.region_repository = RegionRepository(conn)
        self.settlement_repository = SettlementRepository(conn)
        self.npc_repository = NPCRepository(conn)
        self.race_repository = RaceRepository(conn)
        self.relationship_repository = RelationshipRepository(conn)
        self.route_repository = RouteRepository(conn)
        self.event_definition_repository = EventDefinitionRepository(conn)
        self.event_instance_repository = EventInstanceRepository(conn)

    def create_world(self, world: World) -> None:
        existing = self.world_repository.get(world.id)
        if existing:
            raise ValueError(f"World with id {world.id} already exists")
        self.world_repository.add(world)

    def load_world(self, world_id: str) -> Optional[World]:
        return self.world_repository.get(world_id)

    def load_continent(self, continent_id: str) -> Optional[Continent]:
        return self.continent_repository.get(continent_id)

    def load_empire(self, empire_id: str) -> Optional[Empire]:
        return self.empire_repository.get(empire_id)

    def load_kingdom(self, kingdom_id: str) -> Optional[Kingdom]:
        return self.kingdom_repository.get(kingdom_id)

    def load_region(self, region_id: str) -> Optional[Region]:
        return self.region_repository.get(region_id)

    def load_settlement(self, settlement_id: str) -> Optional[SettlementNode]:
        return self.settlement_repository.get(settlement_id)

    def load_npc(self, npc_id: str) -> Optional[NPC]:
        return self.npc_repository.get(npc_id)

    def list_worlds(self) -> list[World]:
        return self.world_repository.list()

    def update_world(self, world: World) -> None:
        self.world_repository.update(world)

    def update_continent(self, continent: Continent) -> None:
        self.continent_repository.update(continent)

    def update_empire(self, empire: Empire) -> None:
        self.empire_repository.update(empire)

    def update_kingdom(self, kingdom: Kingdom) -> None:
        self.kingdom_repository.update(kingdom)

    def update_region(self, region: Region) -> None:
        self.region_repository.update(region)

    def update_settlement(self, settlement: SettlementNode) -> None:
        self.settlement_repository.update(settlement)

    def list_continents(self, world_id: str) -> list[Continent]:
        return self.continent_repository.list_by_world(world_id)

    def list_empires(self, world_id: str) -> list[Empire]:
        return self.empire_repository.list_by_world(world_id)

    def list_kingdoms(self, world_id: str) -> list[Kingdom]:
        return self.kingdom_repository.list_by_world(world_id)

    def list_regions(self, world_id: str) -> list[Region]:
        return self.region_repository.list_by_world(world_id)

    def list_settlements(self, world_id: str) -> list[SettlementNode]:
        return self.settlement_repository.list_by_world(world_id)

    def list_npcs(self, world_id: str) -> list[NPC]:
        return self.npc_repository.list_by_world(world_id)

    def list_relationships(self, world_id: str) -> list[Relationship]:
        return self.relationship_repository.list_by_world(world_id)

    def list_routes(self, world_id: str) -> list[Route]:
        return self.route_repository.list_by_world(world_id)

    def list_event_definitions(self, world_id: str) -> list[EventDefinition]:
        return self.event_definition_repository.list_by_world(world_id)

    def list_event_instances(self, world_id: str) -> list[EventInstance]:
        return self.event_instance_repository.list_by_world(world_id)

    def list_races(self) -> list[Race]:
        return self.race_repository.list()

    def create_continent(self, continent: Continent) -> None:
        self.continent_repository.add(continent)

    def create_empire(self, empire: Empire) -> None:
        self.empire_repository.add(empire)

    def create_kingdom(self, kingdom: Kingdom) -> None:
        self.kingdom_repository.add(kingdom)

    def create_region(self, region: Region) -> None:
        self.region_repository.add(region)

    def create_settlement(self, settlement: SettlementNode) -> None:
        self.settlement_repository.add(settlement)

    def create_npc(self, npc: NPC) -> None:
        self.npc_repository.add(npc)

    def create_relationship(self, relationship: Relationship) -> None:
        self.relationship_repository.add(relationship)

    def create_route(self, route: Route) -> None:
        self.route_repository.add(route)

    def create_event_definition(self, definition: EventDefinition) -> None:
        self.event_definition_repository.add(definition)

    def create_event_instance(self, instance: EventInstance) -> None:
        self.event_instance_repository.add(instance)

    def load_full_world(self, world_id: str) -> dict[str, object]:
        world = self.load_world(world_id)
        if not world:
            raise ValueError(f"World {world_id} not found")
        return {
            "world": world,
            "continents": self.list_continents(world_id),
            "empires": self.list_empires(world_id),
            "kingdoms": self.list_kingdoms(world_id),
            "regions": self.list_regions(world_id),
            "settlements": self.list_settlements(world_id),
        }

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from app.data.jsonio.schema import JsonPackage
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
from app.data.repositories.base import Repository
from app.domain.events.event import EventDefinition, EventInstance
from app.domain.models.serialization import deserialize_dataclass
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


class JsonImporter:
    def __init__(
        self,
        world_repository: WorldRepository,
        continent_repository: ContinentRepository,
        empire_repository: EmpireRepository,
        kingdom_repository: KingdomRepository,
        region_repository: RegionRepository,
        settlement_repository: SettlementRepository,
        npc_repository: NPCRepository,
        relationship_repository: RelationshipRepository,
        route_repository: RouteRepository,
        event_definition_repository: EventDefinitionRepository,
        event_instance_repository: EventInstanceRepository,
    ):
        self.world_repository = world_repository
        self.continent_repository = continent_repository
        self.empire_repository = empire_repository
        self.kingdom_repository = kingdom_repository
        self.region_repository = region_repository
        self.settlement_repository = settlement_repository
        self.npc_repository = npc_repository
        self.relationship_repository = relationship_repository
        self.route_repository = route_repository
        self.event_definition_repository = event_definition_repository
        self.event_instance_repository = event_instance_repository

    def from_file(self, path: Path) -> JsonPackage:
        return JsonPackage.from_json(path.read_text(encoding="utf-8"))

    def import_package(self, package: JsonPackage, overwrite: bool = False) -> World:
        if package.package_type != "world":
            raise ValueError(f"Unsupported import package type: {package.package_type}")

        payload = package.payload
        world_data = payload["world"]
        world = World.from_dict(world_data)

        if self.world_repository.get(world.id) is None:
            self.world_repository.add(world)
        elif overwrite:
            self.world_repository.update(world)
        else:
            raise ValueError(f"World with id {world.id} already exists")

        self._import_entities(payload.get("continents", []), self.continent_repository, Continent)
        self._import_entities(payload.get("empires", []), self.empire_repository, Empire)
        self._import_entities(payload.get("kingdoms", []), self.kingdom_repository, Kingdom)
        self._import_entities(payload.get("regions", []), self.region_repository, Region)
        self._import_entities(payload.get("settlements", []), self.settlement_repository, SettlementNode)
        self._import_entities(payload.get("npcs", []), self.npc_repository, NPC)
        self._import_entities(payload.get("relationships", []), self.relationship_repository, Relationship)
        self._import_entities(payload.get("routes", []), self.route_repository, Route)
        self._import_entities(payload.get("event_definitions", []), self.event_definition_repository, EventDefinition)
        self._import_entities(payload.get("event_instances", []), self.event_instance_repository, EventInstance)

        return world

    def _import_entities(
        self,
        raw_entities: Iterable[dict],
        repository: Repository,
        model_cls: type,
    ) -> None:
        for raw in raw_entities:
            if hasattr(model_cls, "from_dict"):
                entity = model_cls.from_dict(raw)
            else:
                entity = deserialize_dataclass(model_cls, raw)
            if repository.get(entity.id) is None:
                repository.add(entity)
            else:
                repository.update(entity)

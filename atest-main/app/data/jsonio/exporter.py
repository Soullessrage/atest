from __future__ import annotations

from pathlib import Path
from typing import Iterable

from app.data.jsonio.schema import JsonPackage
from app.domain.events.event import EventDefinition, EventInstance
from app.domain.models import (
    Continent,
    Empire,
    Kingdom,
    Relationship,
    Route,
    NPC,
    Region,
    SettlementNode,
    World,
)


class JsonExporter:
    def export_world(self, world: World) -> JsonPackage:
        payload = {
            "world": world.to_dict(),
            "partial": True,
        }
        return JsonPackage(package_type="world", version=1, payload=payload)

    def export_full_world(
        self,
        world: World,
        continents: Iterable[Continent],
        empires: Iterable[Empire],
        kingdoms: Iterable[Kingdom],
        regions: Iterable[Region],
        settlements: Iterable[SettlementNode],
        npcs: Iterable[NPC],
        relationships: Iterable[Relationship],
        routes: Iterable[Route],
        event_definitions: Iterable[EventDefinition],
        event_instances: Iterable[EventInstance],
    ) -> JsonPackage:
        payload = {
            "world": world.to_dict(),
            "continents": [continent.to_dict() for continent in continents],
            "empires": [empire.to_dict() for empire in empires],
            "kingdoms": [kingdom.to_dict() for kingdom in kingdoms],
            "regions": [region.to_dict() for region in regions],
            "settlements": [settlement.to_dict() for settlement in settlements],
            "npcs": [npc.to_dict() for npc in npcs],
            "relationships": [relationship.to_dict() for relationship in relationships],
            "routes": [route.to_dict() for route in routes],
            "event_definitions": [definition.to_dict() for definition in event_definitions],
            "event_instances": [instance.to_dict() for instance in event_instances],
        }
        return JsonPackage(package_type="world", version=1, payload=payload)

    def to_file(self, package: JsonPackage, path: Path) -> None:
        package.to_json(path)

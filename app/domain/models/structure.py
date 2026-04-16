from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from .entity import Entity, IdentifiableReference


class SettlementType(str, Enum):
    VILLAGE = "village"
    TOWN = "town"
    CITY = "city"
    CAPITAL = "capital"
    FORTRESS = "fortress"


@dataclass
class Route(Entity):
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    distance: float = 0.0
    route_type: str = "road"
    notes: str = ""


@dataclass
class PointOfInterest(Entity):
    node_id: Optional[str] = None
    category: str = "milestone"
    importance: int = 1
    influence_scope: List[str] = field(default_factory=list)


@dataclass
class SettlementNode(Entity):
    settlement_type: str = SettlementType.VILLAGE.value
    population: int = 0
    region_id: Optional[str] = None
    kingdom_id: Optional[str] = None
    empire_id: Optional[str] = None
    continent_id: Optional[str] = None
    world_id: Optional[str] = None
    location: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    connected_routes: List[str] = field(default_factory=list)
    points_of_interest: List[PointOfInterest] = field(default_factory=list)
    housing_summary: Dict[str, int] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class Region(Entity):
    kingdom_id: Optional[str] = None
    empire_id: Optional[str] = None
    continent_id: Optional[str] = None
    world_id: Optional[str] = None
    settlement_ids: List[str] = field(default_factory=list)
    point_of_interest_ids: List[str] = field(default_factory=list)


@dataclass
class Kingdom(Entity):
    empire_id: Optional[str] = None
    continent_id: Optional[str] = None
    world_id: Optional[str] = None
    region_ids: List[str] = field(default_factory=list)
    capital_settlement_id: Optional[str] = None


@dataclass
class Empire(Entity):
    continent_id: Optional[str] = None
    world_id: Optional[str] = None
    kingdom_ids: List[str] = field(default_factory=list)
    ruler_name: Optional[str] = None


@dataclass
class Continent(Entity):
    world_id: Optional[str] = None
    empire_ids: List[str] = field(default_factory=list)
    kingdom_ids: List[str] = field(default_factory=list)
    region_ids: List[str] = field(default_factory=list)
    settlement_ids: List[str] = field(default_factory=list)


@dataclass
class World(Entity):
    continents: List[str] = field(default_factory=list)
    empires: List[str] = field(default_factory=list)
    kingdoms: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    settlements: List[str] = field(default_factory=list)
    npc_ids: List[str] = field(default_factory=list)
    event_ids: List[str] = field(default_factory=list)
    rule_set_id: Optional[str] = None

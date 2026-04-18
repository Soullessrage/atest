"""Repository interfaces and helpers for domain persistence."""

from .continent_repository import ContinentRepository
from .empire_repository import EmpireRepository
from .event_repository import EventDefinitionRepository, EventInstanceRepository
from .kingdom_repository import KingdomRepository
from .npc_repository import NPCRepository
from .race_repository import RaceRepository
from .relationship_repository import RelationshipRepository
from .region_repository import RegionRepository
from .route_repository import RouteRepository
from .settlement_repository import SettlementRepository
from .world_repository import WorldRepository

__all__ = [
    "ContinentRepository",
    "EmpireRepository",
    "EventDefinitionRepository",
    "EventInstanceRepository",
    "KingdomRepository",
    "NPCRepository",
    "RaceRepository",
    "RelationshipRepository",
    "RegionRepository",
    "RouteRepository",
    "SettlementRepository",
    "WorldRepository",
]

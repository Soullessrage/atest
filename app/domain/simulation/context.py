"""Simulation context carries state and results through simulation passes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List

from app.domain.models.structure import World


@dataclass
class SimulationChanges:
    """Tracks changes made during simulation for reporting and undo."""

    npc_aged: List[str] = field(default_factory=list)
    npc_died: List[str] = field(default_factory=list)
    npc_born: List[str] = field(default_factory=list)
    npcs_migrated: List[tuple[str, str, str]] = field(default_factory=list)  # (npc_id, from_settlement, to_settlement)
    relationships_formed: List[tuple[str, str]] = field(default_factory=list)  # (source_id, target_id)
    relationships_decayed: List[str] = field(default_factory=list)  # relationship_ids
    settlements_grew: List[tuple[str, int, int]] = field(default_factory=list)  # (settlement_id, old_pop, new_pop)
    settlements_shrunk: List[tuple[str, int, int]] = field(default_factory=list)  # (settlement_id, old_pop, new_pop)
    events_triggered: List[str] = field(default_factory=list)  # event_instance_ids
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationContext:
    """
    Carries world state and simulation metadata through passes.

    Each pass receives this context, modifies the world state, and records changes.
    The context is immutable for a given pass (no shared state modifications between passes).
    """

    world: World
    world_datetime: datetime
    duration: timedelta
    changes: SimulationChanges = field(default_factory=SimulationChanges)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def advance_datetime_by_days(self, days: int) -> None:
        """Advance the simulation datetime by N days."""
        self.world_datetime = self.world_datetime + timedelta(days=days)

    def record_npc_aged(self, npc_id: str) -> None:
        """Record that an NPC aged."""
        if npc_id not in self.changes.npc_aged:
            self.changes.npc_aged.append(npc_id)

    def record_npc_death(self, npc_id: str) -> None:
        """Record that an NPC died."""
        if npc_id not in self.changes.npc_died:
            self.changes.npc_died.append(npc_id)

    def record_npc_birth(self, npc_id: str) -> None:
        """Record that an NPC was born."""
        if npc_id not in self.changes.npc_born:
            self.changes.npc_born.append(npc_id)

    def record_npc_migration(self, npc_id: str, from_settlement_id: str, to_settlement_id: str) -> None:
        """Record that an NPC migrated."""
        self.changes.npcs_migrated.append((npc_id, from_settlement_id, to_settlement_id))

    def record_relationship_formed(self, source_id: str, target_id: str) -> None:
        """Record that a relationship was formed."""
        self.changes.relationships_formed.append((source_id, target_id))

    def record_relationship_decayed(self, relationship_id: str) -> None:
        """Record that a relationship decayed."""
        if relationship_id not in self.changes.relationships_decayed:
            self.changes.relationships_decayed.append(relationship_id)

    def record_settlement_growth(self, settlement_id: str, old_pop: int, new_pop: int) -> None:
        """Record that a settlement grew."""
        if new_pop > old_pop:
            self.changes.settlements_grew.append((settlement_id, old_pop, new_pop))

    def record_settlement_shrinkage(self, settlement_id: str, old_pop: int, new_pop: int) -> None:
        """Record that a settlement shrank."""
        if new_pop < old_pop:
            self.changes.settlements_shrunk.append((settlement_id, old_pop, new_pop))

    def record_event(self, event_instance_id: str) -> None:
        """Record that an event was triggered."""
        if event_instance_id not in self.changes.events_triggered:
            self.changes.events_triggered.append(event_instance_id)

    def set_metadata(self, key: str, value: Any) -> None:
        """Store metadata accessible to all passes."""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Retrieve metadata."""
        return self.metadata.get(key, default)

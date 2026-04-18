"""Relationship dynamics simulation passes."""

from __future__ import annotations

import random
from typing import Optional

from app.core.services.persistence_service import PersistenceService
from app.domain.models.relationship import Relationship
from app.domain.simulation.context import SimulationContext
from app.domain.simulation.pass_engine import SimulationPass


class RelationshipDynamicsPass(SimulationPass):
    """
    Simulates changes to NPC relationships over time.
    
    Relationships can:
    - Strengthen (through proximity, shared experience, common interests)
    - Weaken/decay (through distance, betrayal, time)
    - Form new (through events, mutual acquaintances, proximity)
    - Break (through betrayal, death, abandonment)
    """

    def __init__(self, persistence_service: Optional[PersistenceService] = None):
        super().__init__("Relationship Dynamics")
        self.persistence_service = persistence_service

    def apply(self, context: SimulationContext) -> None:
        """Update existing relationships and form new ones."""
        if not self.persistence_service:
            return

        relationships = self.persistence_service.list_relationships(context.world.id)
        npcs = self.persistence_service.list_npcs(context.world.id)

        # Update existing relationships
        for rel in relationships:
            if rel is None:
                continue

            source = next((n for n in npcs if n and n.id == rel.source_id), None)
            target = next((n for n in npcs if n and n.id == rel.target_id), None)

            if not source or not target:
                continue

            old_weight = rel.weight

            # Proximity boost - same settlement increases relationship weight
            if source.settlement_id == target.settlement_id:
                rel.weight = min(rel.weight + 0.5, 100.0)
            else:
                # Distance decay - different settlements decreases relationship weight
                rel.weight = max(rel.weight - 0.3, 0.0)

            # Family relationships are stable
            if rel.relation_type in ["family", "marriage", "partnership"]:
                rel.weight = min(rel.weight + 0.1, 100.0)
            # Rivalries can intensify or fade
            elif rel.relation_type == "rivalry":
                if random.random() < 0.3:  # 30% chance to intensify
                    rel.weight = min(rel.weight + 0.2, 100.0)
                else:  # Otherwise decay
                    rel.weight = max(rel.weight - 0.1, 0.0)
            # Neutral relationships slowly decay
            elif rel.relation_type in ["acquaintance", "neutral"]:
                rel.weight = max(rel.weight - 0.2, 0.0)

            # Record change
            if rel.weight != old_weight:
                if rel.weight > old_weight:
                    pass  # Strengthened (could log separately)
                elif rel.weight == 0:
                    context.record_relationship_decayed(rel.id)
                else:
                    pass  # Weakened (could log separately)

            # Record in history
            if rel.history is None:
                rel.history = []
            rel.history.append(f"Weight: {old_weight:.1f} → {rel.weight:.1f}")

        # Form new relationships based on proximity
        self._form_new_relationships(npcs, context)

    def _form_new_relationships(self, npcs: list, context: SimulationContext) -> None:
        """Form new relationships between NPCs in same settlement."""
        if not self.persistence_service:
            return

        # Group NPCs by settlement
        by_settlement = {}
        for npc in npcs:
            if npc and npc.settlement_id:
                if npc.settlement_id not in by_settlement:
                    by_settlement[npc.settlement_id] = []
                by_settlement[npc.settlement_id].append(npc)

        # For each settlement, randomly form new relationships
        for settlement_id, settlement_npcs in by_settlement.items():
            if len(settlement_npcs) < 2:
                continue

            # Chance of new relationship forming in each settlement
            if random.random() > 0.15:  # 15% chance per period
                continue

            # Pick two random NPCs
            npc1, npc2 = random.sample(settlement_npcs, 2)

            # Check if relationship already exists
            existing = self.persistence_service.relationship_repository.find_between(npc1.id, npc2.id)
            if existing:
                continue

            # Determine relationship type
            rel_type = random.choice(["acquaintance", "friendship", "neutral"])
            initial_weight = random.uniform(10, 30)  # New relationships start weak

            new_rel = Relationship(
                world_id=context.world.id,
                source_id=npc1.id,
                target_id=npc2.id,
                relation_type=rel_type,
                weight=initial_weight,
                history=[f"Met in {settlement_id}"],
            )

            self.persistence_service.relationship_repository.create(new_rel)
            context.record_relationship_formed(npc1.id, npc2.id)


class RelationshipDecayPass(SimulationPass):
    """
    Simulates relationships ending or becoming irrelevant over time.
    
    Very weak relationships (weight near 0) can be pruned.
    Dead NPCs' relationships are removed.
    """

    def __init__(self, persistence_service: Optional[PersistenceService] = None):
        super().__init__("Relationship Decay")
        self.persistence_service = persistence_service

    def apply(self, context: SimulationContext) -> None:
        """Remove dead relationships."""
        if not self.persistence_service:
            return

        relationships = self.persistence_service.list_relationships(context.world.id)
        dead_npc_ids = set(context.changes.npc_died)

        # Remove relationships involving dead NPCs
        for rel in relationships:
            if rel and (rel.source_id in dead_npc_ids or rel.target_id in dead_npc_ids):
                context.record_relationship_decayed(rel.id)
                # Mark for deletion (persistence layer handles actual removal)

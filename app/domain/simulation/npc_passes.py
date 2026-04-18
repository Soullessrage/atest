"""NPC lifecycle simulation passes (aging, death, births)."""

from __future__ import annotations

import random
from typing import List, Optional

from app.core.services.persistence_service import PersistenceService
from app.domain.models.npc import NPC
from app.domain.models.relationship import Relationship
from app.domain.simulation.context import SimulationContext
from app.domain.simulation.pass_engine import SimulationPass


class NPCAgeingPass(SimulationPass):
    """
    Ages all NPCs in the world by the simulation duration.
    
    Updates NPC ages based on the number of days that passed.
    """

    def __init__(self, persistence_service: Optional[PersistenceService] = None):
        super().__init__("NPC Ageing")
        self.persistence_service = persistence_service

    def apply(self, context: SimulationContext) -> None:
        """Age all NPCs."""
        # Calculate years passed
        years_passed = context.duration.days / 365.0

        # Get all NPCs in the world
        if self.persistence_service:
            npcs = self.persistence_service.list_npcs(context.world.id)
        else:
            # Fallback for testing: get from world if persistence not available
            npcs = getattr(context.world, "_npcs", [])

        for npc in npcs:
            if npc and years_passed >= 1:
                npc.age += int(years_passed)
                context.record_npc_aged(npc.id)


class NPCDeathPass(SimulationPass):
    """
    Evaluates NPC mortality based on age and race lifespan.
    
    Uses race definitions to determine natural lifespan and applies mortality chance
    based on how long the NPC has lived relative to their race's max lifespan.
    """

    def __init__(self, persistence_service: Optional[PersistenceService] = None):
        super().__init__("NPC Death")
        self.persistence_service = persistence_service
        self.base_lifespan = 80  # Default human lifespan in years

    def apply(self, context: SimulationContext) -> None:
        """Evaluate NPC deaths."""
        if not self.persistence_service:
            return  # Can't determine lifespans without persistence

        npcs = self.persistence_service.list_npcs(context.world.id)
        npcs_to_remove = []

        for npc in npcs:
            if npc is None:
                continue

            # Get lifespan for NPC's race
            lifespan = self._get_lifespan_for_npc(npc)

            # If NPC exceeded natural lifespan, they have a chance to die each year
            if npc.age >= lifespan:
                # Mortality chance increases significantly after natural lifespan
                years_over = npc.age - lifespan
                mortality_chance = 0.05 + (years_over * 0.1)  # Start at 5%, increase 10% per year over
                mortality_chance = min(mortality_chance, 0.95)  # Cap at 95%

                if random.random() < mortality_chance:
                    npcs_to_remove.append(npc.id)
                    context.record_npc_death(npc.id)
            elif npc.age >= lifespan * 0.9:
                # Even before exceeding lifespan, small chance to die from illness/accident
                if random.random() < 0.02:  # 2% chance per simulation run
                    npcs_to_remove.append(npc.id)
                    context.record_npc_death(npc.id)

        # Remove dead NPCs from world
        if context.world.npc_ids:
            for npc_id in npcs_to_remove:
                if npc_id in context.world.npc_ids:
                    context.world.npc_ids.remove(npc_id)

    def _get_lifespan_for_npc(self, npc: NPC) -> int:
        """Get the natural lifespan for an NPC based on their race."""
        if npc.race_id and self.persistence_service:
            race = self.persistence_service.race_repository.get(npc.race_id)
            if race and hasattr(race, "lifespan") and race.lifespan:
                return race.lifespan
        return self.base_lifespan


class NPCBirthPass(SimulationPass):
    """
    Simulates NPC births based on relationship fertility and population capacity.
    
    Evaluates fertile relationships and creates new NPCs based on:
    - Relationship proximity and type (married/partners)
    - Fertility scores
    - Settlement population capacity
    - Background birth rate configuration
    """

    def __init__(self, persistence_service: Optional[PersistenceService] = None, birth_rate: float = 0.05):
        super().__init__("NPC Birth")
        self.persistence_service = persistence_service
        self.birth_rate = birth_rate  # Births per fertile adult per simulation period

    def apply(self, context: SimulationContext) -> None:
        """Evaluate and create NPC births."""
        if not self.persistence_service:
            return

        npcs = self.persistence_service.list_npcs(context.world.id)
        relationships = self.persistence_service.list_relationships(context.world.id)

        # Ensure npc_ids list exists
        if context.world.npc_ids is None:
            context.world.npc_ids = []

        # Find fertile partnerships
        fertile_pairs = self._find_fertile_relationships(npcs, relationships)

        for source_id, target_id in fertile_pairs:
            source = next((n for n in npcs if n and n.id == source_id), None)
            target = next((n for n in npcs if n and n.id == target_id), None)

            if not source or not target:
                continue

            # Determine birth chance based on fertility and relationship weight
            relationship = next(
                (r for r in relationships if r and r.source_id == source_id and r.target_id == target_id),
                None,
            )

            if relationship:
                # Birth chance increases with relationship weight
                base_chance = self.birth_rate * (relationship.weight / 100.0)  # Assuming weight 0-100

                if random.random() < base_chance:
                    # Create new NPC (baby)
                    new_npc = self._create_baby_npc(source, target, context)
                    if new_npc:
                        context.world.npc_ids.append(new_npc.id)
                        context.record_npc_birth(new_npc.id)

                        # Add family relationship
                        if hasattr(new_npc, "family_ids"):
                            if not new_npc.family_ids:
                                new_npc.family_ids = []
                            new_npc.family_ids.extend([source_id, target_id])

    def _find_fertile_relationships(
        self, npcs: List[NPC], relationships: List[Relationship]
    ) -> List[tuple[str, str]]:
        """Find relationships that could produce offspring."""
        fertile_pairs = []

        for rel in relationships:
            if rel is None:
                continue

            # Look for partner/marriage type relationships with good weight
            if rel.relation_type in ["marriage", "partnership"] and rel.weight > 50:
                source = next((n for n in npcs if n and n.id == rel.source_id), None)
                target = next((n for n in npcs if n and n.id == rel.target_id), None)

                if self._can_reproduce(source) and self._can_reproduce(target):
                    fertile_pairs.append((rel.source_id, rel.target_id))

        return fertile_pairs

    def _can_reproduce(self, npc: Optional[NPC]) -> bool:
        """Check if an NPC can reproduce."""
        if not npc:
            return False

        # Age requirements (roughly 16-55 for females, 18-70 for males in most fantasy settings)
        if npc.age < 16 or npc.age > 75:
            return False

        # Health check
        if npc.health_status in ["dead", "terminally_ill", "infertile"]:
            return False

        # Fertility score (if set)
        if hasattr(npc, "fertility_score") and npc.fertility_score is not None:
            if npc.fertility_score <= 0:
                return False

        return True

    def _create_baby_npc(self, parent1: NPC, parent2: NPC, context: SimulationContext) -> Optional[NPC]:
        """Create a new NPC as the child of two parents."""
        from uuid import uuid4

        settlement_id = parent1.settlement_id or parent2.settlement_id

        baby = NPC(
            id=str(uuid4()),
            name=f"{parent1.name or 'Unknown'}'s Child",
            world_id=context.world.id,
            settlement_id=settlement_id,
            age=0,  # Newborn
            race_id=random.choice([parent1.race_id, parent2.race_id]) if parent1.race_id or parent2.race_id else None,
            health_status="healthy",
        )

        return baby

"""Population and settlement dynamics simulation passes."""

from __future__ import annotations

import random
from typing import Optional

from app.core.services.persistence_service import PersistenceService
from app.domain.models.structure import SettlementNode
from app.domain.simulation.context import SimulationContext
from app.domain.simulation.pass_engine import SimulationPass


class PopulationDynamicsPass(SimulationPass):
    """
    Updates settlement populations based on NPC counts and births/deaths.
    
    This pass calculates settlement population from actual NPC residents
    and applies growth or decline factors.
    """

    def __init__(self, persistence_service: Optional[PersistenceService] = None):
        super().__init__("Population Dynamics")
        self.persistence_service = persistence_service

    def apply(self, context: SimulationContext) -> None:
        """Update settlement populations."""
        if not self.persistence_service:
            return

        settlements = self.persistence_service.list_settlements(context.world.id)
        npcs = self.persistence_service.list_npcs(context.world.id)

        # Track NPCs by settlement
        npc_count_by_settlement = {}
        for npc in npcs:
            if npc and npc.settlement_id:
                npc_count_by_settlement[npc.settlement_id] = npc_count_by_settlement.get(npc.settlement_id, 0) + 1

        for settlement in settlements:
            if not settlement:
                continue

            old_pop = settlement.population
            resident_npcs = npc_count_by_settlement.get(settlement.id, 0)

            # Calculate population from actual NPC residents plus estimated families/commoners
            # Assume each NPC represents a household of ~3-4 people on average
            calculated_pop = resident_npcs * 3

            # Apply growth/decline factors
            new_pop = self._apply_growth_factors(calculated_pop, settlement, context)

            if new_pop != old_pop:
                settlement.population = new_pop

                if new_pop > old_pop:
                    context.record_settlement_growth(settlement.id, old_pop, new_pop)
                else:
                    context.record_settlement_shrinkage(settlement.id, old_pop, new_pop)

    def _apply_growth_factors(self, base_pop: int, settlement: SettlementNode, context: SimulationContext) -> int:
        """Apply growth/decline modifiers based on settlement conditions."""
        years = context.duration.days / 365.0

        # Start with base population
        pop = base_pop

        # Growth factors
        growth_rate = 0.03  # 3% annual growth by default

        # Settlement type affects growth
        if settlement.settlement_type == "city":
            growth_rate = 0.05  # Cities grow faster
        elif settlement.settlement_type == "village":
            growth_rate = 0.02  # Villages grow slower
        elif settlement.settlement_type == "fortress":
            growth_rate = 0.01  # Fortresses are military, limited growth

        # Apply growth over time
        pop = int(pop * (1 + growth_rate) ** years)

        # Random events can affect population
        if random.random() < 0.1:  # 10% chance of a population event
            event_pop = int(pop * random.uniform(0.95, 1.05))  # ±5% variation
            pop = event_pop

        return max(pop, 0)  # Population can't go negative


class SettlementGrowthPass(SimulationPass):
    """
    Evaluates conditions for settlement emergence and development.
    
    Settlements can emerge from:
    - Sudden population influx (refugee crisis, migration wave)
    - Valuable resources discovered
    - Trade route crossings
    
    Settlements can be upgraded:
    - Village → Town (population > 1000)
    - Town → City (population > 5000)
    """

    def __init__(self, persistence_service: Optional[PersistenceService] = None):
        super().__init__("Settlement Growth")
        self.persistence_service = persistence_service

    def apply(self, context: SimulationContext) -> None:
        """Evaluate settlement upgrades and emergence."""
        if not self.persistence_service:
            return

        settlements = self.persistence_service.list_settlements(context.world.id)

        for settlement in settlements:
            if not settlement:
                continue

            # Upgrade settlements based on population
            old_type = settlement.settlement_type

            if settlement.population >= 5000 and settlement.settlement_type != "city":
                settlement.settlement_type = "city"
            elif settlement.population >= 1000 and settlement.settlement_type == "village":
                settlement.settlement_type = "town"

            # Record if type changed
            if old_type != settlement.settlement_type:
                context.set_metadata(
                    f"settlement_upgraded_{settlement.id}",
                    {"from": old_type, "to": settlement.settlement_type},
                )


class MigrationPass(SimulationPass):
    """
    Simulates NPC migration based on opportunity and hardship.
    
    NPCs may migrate to:
    - Settlements with better opportunities (larger, safer, etc.)
    - Away from settlements experiencing hardship (war, plague, famine)
    """

    def __init__(self, persistence_service: Optional[PersistenceService] = None, migration_rate: float = 0.05):
        super().__init__("Migration")
        self.persistence_service = persistence_service
        self.migration_rate = migration_rate  # % of NPCs who might migrate per period

    def apply(self, context: SimulationContext) -> None:
        """Evaluate NPC migrations."""
        if not self.persistence_service:
            return

        npcs = self.persistence_service.list_npcs(context.world.id)
        settlements = self.persistence_service.list_settlements(context.world.id)

        if not settlements:
            return

        for npc in npcs:
            if not npc or not npc.settlement_id:
                continue

            # Check if NPC might migrate
            if random.random() > self.migration_rate:
                continue

            current_settlement = next((s for s in settlements if s and s.id == npc.settlement_id), None)
            if not current_settlement:
                continue

            # Find a better settlement (simple: just pick a larger one)
            better_settlements = [s for s in settlements if s and s.population > current_settlement.population]

            if better_settlements:
                new_settlement = random.choice(better_settlements)
                old_id = npc.settlement_id
                npc.settlement_id = new_settlement.id

                context.record_npc_migration(npc.id, old_id, new_settlement.id)

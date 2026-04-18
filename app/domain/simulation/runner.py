from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from app.core.services.persistence_service import PersistenceService
from app.domain.events.engine import EventEngine
from app.domain.events.event import EventDefinition, EventInstance
from app.domain.models.structure import World
from app.domain.simulation.context import SimulationContext, SimulationChanges
from app.domain.simulation.pass_engine import SimulationPassEngine
from app.domain.simulation.npc_passes import NPCAgeingPass, NPCDeathPass, NPCBirthPass
from app.domain.simulation.population_passes import PopulationDynamicsPass, SettlementGrowthPass, MigrationPass
from app.domain.simulation.relationship_passes import RelationshipDynamicsPass, RelationshipDecayPass


class SimulationRun:
    """Result of a simulation run, containing changes and events."""

    def __init__(self, world: World, duration: timedelta, context: SimulationContext):
        self.world = world
        self.duration = duration
        self.changes: SimulationChanges = context.changes
        self.events: List[EventInstance] = []
        self.created_at = datetime.utcnow()


class SimulationRunner:
    """
    Orchestrates world simulation through a sequence of simulation passes.

    The runner:
    1. Creates a SimulationContext with current world state
    2. Executes all simulation passes in order (aging, death, births, relationships, events, etc.)
    3. Evaluates events and records what happened
    4. Returns results containing changes and events
    """

    def __init__(
        self,
        world: World,
        persistence_service: Optional[PersistenceService] = None,
        event_definitions: list[EventDefinition] | None = None,
    ):
        self.world = world
        self.persistence_service = persistence_service
        self.event_definitions = event_definitions or []

        # Build the simulation pass engine with all simulation phases
        self.pass_engine = self._build_pass_engine()

    def _build_pass_engine(self) -> SimulationPassEngine:
        """Create the simulation pass engine with all active passes."""
        engine = SimulationPassEngine()

        # Add passes in execution order (critical for correct simulation flow)

        # Phase 1: NPC Lifecycle
        engine.add_pass(NPCAgeingPass(self.persistence_service))
        engine.add_pass(NPCDeathPass(self.persistence_service))
        engine.add_pass(NPCBirthPass(self.persistence_service))

        # Phase 2: Movement and Migration
        engine.add_pass(MigrationPass(self.persistence_service))

        # Phase 3: Relationships
        engine.add_pass(RelationshipDynamicsPass(self.persistence_service))
        engine.add_pass(RelationshipDecayPass(self.persistence_service))

        # Phase 4: Population and Settlements
        engine.add_pass(PopulationDynamicsPass(self.persistence_service))
        engine.add_pass(SettlementGrowthPass(self.persistence_service))

        return engine

    def advance_time(self, duration: timedelta) -> SimulationRun:
        """
        Advance world time by the specified duration.

        Executes all simulation passes and evaluates events.

        Args:
            duration: The timedelta to advance the world by.

        Returns:
            A SimulationRun object containing all changes and events.
        """
        # Create simulation context
        context = SimulationContext(
            world=self.world,
            world_datetime=datetime.utcnow(),
            duration=duration,
        )

        # Execute all simulation passes (this mutates context.world)
        self.pass_engine.execute(context)

        # Evaluate events
        engine = EventEngine(self.event_definitions)
        events = engine.evaluate(context.world_datetime, duration)

        # Create the result
        run = SimulationRun(self.world, duration, context)
        run.events = events

        return run

    def preview(self, duration: timedelta) -> dict:
        """Generate a preview of likely simulation outcomes without executing."""
        context = SimulationContext(
            world=self.world,
            world_datetime=datetime.utcnow(),
            duration=duration,
        )

        # Estimate changes without actually modifying
        return {
            "duration_days": duration.days,
            "estimated_npc_ages": f"+{int(duration.days / 365)} years",
            "estimated_settlement_changes": len(self.world.settlements) * 0.05,
            "potential_events": len(self.event_definitions),
            "estimated_births": int(len(self.world.npc_ids) * 0.02),  # ~2% birth rate
            "estimated_deaths": int(len(self.world.npc_ids) * 0.01),  # ~1% death rate
        }

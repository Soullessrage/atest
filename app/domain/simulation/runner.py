from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from app.domain.events.engine import EventEngine
from app.domain.events.event import EventDefinition, EventInstance
from app.domain.models.structure import World


class SimulationRun:
    def __init__(self, world: World, duration: timedelta):
        self.world = world
        self.duration = duration
        self.events: List[EventInstance] = []
        self.created_at = datetime.utcnow()


class SimulationRunner:
    def __init__(self, world: World, event_definitions: list[EventDefinition] | None = None):
        self.world = world
        self.event_definitions = event_definitions or []

    def advance_time(self, duration: timedelta) -> SimulationRun:
        run = SimulationRun(self.world, duration)
        engine = EventEngine(self.event_definitions)
        run.events = engine.evaluate(run.created_at, duration)
        return run

    def preview(self, duration: timedelta) -> dict:
        return {
            "duration": duration.total_seconds(),
            "estimated_settlement_changes": len(self.world.settlements) * 0.05,
            "estimated_npc_changes": len(self.world.npc_ids) * 0.1,
            "potential_events": len(self.event_definitions),
        }

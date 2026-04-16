from __future__ import annotations

from datetime import timedelta
from sqlite3 import Connection
from typing import Dict

from app.core.services.event_service import EventService
from app.core.services.persistence_service import PersistenceService
from app.domain.simulation.runner import SimulationRunner
from app.domain.models.structure import World


class SimulationService:
    def __init__(self, conn: Connection):
        self.persistence_service = PersistenceService(conn)
        self.event_service = EventService(conn)

    def preview_advance(self, world_id: str, duration: timedelta) -> Dict[str, object]:
        world = self.persistence_service.load_world(world_id)
        if not world:
            raise ValueError(f"World {world_id} not found")
        runner = SimulationRunner(world)
        return runner.preview(duration)

    def advance(self, world_id: str, duration: timedelta) -> Dict[str, object]:
        world = self.persistence_service.load_world(world_id)
        if not world:
            raise ValueError(f"World {world_id} not found")
        runner = SimulationRunner(world)
        run = runner.advance_time(duration)
        return {
            "world_id": world_id,
            "duration": duration.total_seconds(),
            "event_count": len(run.events),
            "outcome_summary": "Simulation advanced with event generation and demographic planning.",
        }

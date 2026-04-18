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
        runner = SimulationRunner(world, persistence_service=self.persistence_service)
        return runner.preview(duration)

    def advance(self, world_id: str, duration: timedelta) -> Dict[str, object]:
        world = self.persistence_service.load_world(world_id)
        if not world:
            raise ValueError(f"World {world_id} not found")
        runner = SimulationRunner(world, persistence_service=self.persistence_service)
        run = runner.advance_time(duration)
        return {
            "world_id": world_id,
            "duration_days": duration.days,
            "event_count": len(run.events),
            "npcs_aged": len(run.changes.npc_aged),
            "npcs_died": len(run.changes.npc_died),
            "npcs_born": len(run.changes.npc_born),
            "settlements_grew": len(run.changes.settlements_grew),
            "settlements_shrunk": len(run.changes.settlements_shrunk),
            "outcome_summary": "Simulation advanced with NPC aging, deaths, births, and demographic changes.",
        }

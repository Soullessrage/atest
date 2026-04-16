from threading import Thread
from app.core.simulation.engine import SimulationEngine
from app.core.events.models import Event

class SimulationService:
    """High-level API for UI to control the simulation."""

    def __init__(self):
        self.engine = SimulationEngine()
        self.thread: Thread | None = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return  # already running

        self.thread = Thread(target=self.engine.start, daemon=True)
        self.thread.start()

    def stop(self):
        self.engine.stop()

    def schedule_event(self, tick: int, type: str, payload, handler):
        event = Event.create(tick, type, payload, handler)
        self.engine.add_event(event)
        return event.id

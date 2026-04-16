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

    def schedule_recurring_event(self, interval, type, payload, handler):
        def wrapper(p):
            handler(p)
            next_tick = self.engine.current_tick + interval
            self.schedule_event(next_tick, type, payload, wrapper)

        first_tick = self.engine.current_tick + interval
        self.schedule_event(first_tick, type, payload, wrapper)

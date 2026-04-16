import time
from typing import List
from app.core.events.models import Event
from app.core.simulation import processors


class SimulationEngine:
    """Core simulation engine that processes events and advances time."""

    def __init__(self, tick_rate: float = 0.1):
        self.current_tick = 0
        self.tick_rate = tick_rate
        self.running = False
        self.event_queue: List[Event] = []

        # Phase 5 world state
        self.state = {
            "towns": {},
            "regions": {},
            "world": {}
        }

    def add_event(self, event: Event):
        self.event_queue.append(event)
        self.event_queue.sort(key=lambda e: e.tick)

    def start(self):
        self.running = True
        while self.running:
            self._process_tick()
            time.sleep(self.tick_rate)

    def stop(self):
        self.running = False

    def _process_tick(self):
        """Process all events scheduled for this tick."""
        events_to_run = [e for e in self.event_queue if e.tick == self.current_tick]

        for event in events_to_run:

            # Route event types to processors
            if event.type == "economy":
                processors.process_economy(self.state, event.payload)

            elif event.type == "population":
                processors.process_population(self.state, event.payload)

            elif event.type == "weather":
                processors.process_weather(self.state, event.payload)

            # Run event handler (UI logging, etc.)
            event.handler(event.payload)

            self.event_queue.remove(event)

        # Advance simulation time
        self.current_tick += 1

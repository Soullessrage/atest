import time
from typing import List
from app.core.events.models import Event

class SimulationEngine:
    """Core simulation engine that processes events and advances time."""

    def __init__(self, tick_rate: float = 0.1):
        self.current_tick = 0
        self.tick_rate = tick_rate
        self.running = False
        self.event_queue: List[Event] = []

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
            event.handler(event.payload)
            self.event_queue.remove(event)

        self.current_tick += 1

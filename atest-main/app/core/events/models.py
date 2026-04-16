from dataclasses import dataclass
from typing import Callable, Any, Dict
import uuid

@dataclass
class Event:
    """A scheduled event in the simulation."""
    id: str
    tick: int
    type: str
    payload: Dict[str, Any]
    handler: Callable

    @staticmethod
    def create(tick: int, type: str, payload: Dict[str, Any], handler: Callable):
        return Event(
            id=str(uuid.uuid4()),
            tick=tick,
            type=type,
            payload=payload,
            handler=handler
        )

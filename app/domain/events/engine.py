from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from app.domain.events.event import EventDefinition, EventInstance


class EventEngine:
    def __init__(self, definitions: List[EventDefinition]):
        self.definitions = definitions

    def evaluate(self, world_datetime: datetime, duration: timedelta) -> List[EventInstance]:
        instances: List[EventInstance] = []
        for definition in self.definitions:
            if definition.probability <= 0:
                continue
            if definition.probability >= 1 or definition.probability > 0 and world_datetime.second % 2 == 0:
                instances.append(
                    EventInstance(
                        definition_id=definition.id,
                        occurred_at=world_datetime,
                        affected_scope=definition.scope,
                        effect_summary=f"Triggered {definition.name}",
                        details={"duration_days": definition.duration_days},
                    )
                )
        return instances

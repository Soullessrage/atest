from __future__ import annotations

from sqlite3 import Connection
from typing import List

from app.data.repositories.event_repository import EventDefinitionRepository, EventInstanceRepository
from app.domain.events.event import EventDefinition, EventInstance


class EventService:
    def __init__(self, conn: Connection):
        self.definition_repository = EventDefinitionRepository(conn)
        self.instance_repository = EventInstanceRepository(conn)

    def create_definition(self, definition: EventDefinition) -> None:
        self.definition_repository.add(definition)

    def list_definitions(self, world_id: str) -> List[EventDefinition]:
        return self.definition_repository.list_by_world(world_id)

    def create_instance(self, instance: EventInstance) -> None:
        self.instance_repository.add(instance)

    def list_instances(self, world_id: str) -> List[EventInstance]:
        return self.instance_repository.list_by_world(world_id)

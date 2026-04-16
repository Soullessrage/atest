from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from app.domain.models.serialization import deserialize_dataclass, serialize_dataclass


@dataclass
class EventCondition:
    expression: str
    parameters: Dict[str, object] = field(default_factory=dict)


@dataclass
class EventDefinition:
    id: str = field(default_factory=lambda: str(uuid4()))
    world_id: Optional[str] = None
    name: str = ""
    description: str = ""
    scope: str = "world"
    category: str = "general"
    probability: float = 0.0
    duration_days: int = 0
    conditions: List[EventCondition] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    locked: bool = False
    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return serialize_dataclass(self)

    @classmethod
    def from_dict(cls, source: Dict[str, object]) -> "EventDefinition":
        return deserialize_dataclass(cls, source)


@dataclass
class EventInstance:
    id: str = field(default_factory=lambda: str(uuid4()))
    definition_id: str = ""
    world_id: Optional[str] = None
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    affected_scope: str = "world"
    effect_summary: str = ""
    details: Dict[str, object] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    locked: bool = False
    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return serialize_dataclass(self)

    @classmethod
    def from_dict(cls, source: Dict[str, object]) -> "EventInstance":
        return deserialize_dataclass(cls, source)

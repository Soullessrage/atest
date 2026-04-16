from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from .serialization import deserialize_dataclass, serialize_dataclass


@dataclass
class Entity:
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    locked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()

    def lock(self) -> None:
        self.locked = True

    def unlock(self) -> None:
        self.locked = False

    def to_dict(self) -> Dict[str, Any]:
        return serialize_dataclass(self)

    @classmethod
    def from_dict(cls, source: Dict[str, Any]):
        return deserialize_dataclass(cls, source)


@dataclass
class IdentifiableReference:
    id: str
    type_name: str

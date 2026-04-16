from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.domain.models.entity import Entity


@dataclass
class Relationship(Entity):
    world_id: Optional[str] = None
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    relation_type: str = "acquaintance"
    weight: float = 0.0
    history: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

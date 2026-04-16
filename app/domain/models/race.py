from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.domain.models.entity import Entity


@dataclass
class Race(Entity):
    cultural_tags: List[str] = field(default_factory=list)
    lifespan: Optional[int] = None
    preferred_occupations: List[str] = field(default_factory=list)
    settlement_preferences: List[str] = field(default_factory=list)


@dataclass
class SubRace(Entity):
    race_id: Optional[str] = None
    modifiers: Dict[str, object] = field(default_factory=dict)

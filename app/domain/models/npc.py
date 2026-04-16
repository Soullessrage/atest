from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.domain.models.entity import Entity


@dataclass
class NPC(Entity):
    world_id: Optional[str] = None
    settlement_id: Optional[str] = None
    age: int = 0
    gender: Optional[str] = None
    race_id: Optional[str] = None
    subrace_id: Optional[str] = None
    occupation: Optional[str] = None
    social_role: Optional[str] = None
    residence_id: Optional[str] = None
    wealth_status: Optional[str] = None
    personality_traits: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    motivations: List[str] = field(default_factory=list)
    flaws: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)
    family_ids: List[str] = field(default_factory=list)
    relationship_ids: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    health_status: Optional[str] = None
    injuries: List[str] = field(default_factory=list)
    illnesses: List[str] = field(default_factory=list)
    fertility_score: Optional[float] = None

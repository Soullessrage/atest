from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RuleSet:
    id: str
    name: str
    description: str = ""
    version: int = 1
    options: Dict[str, object] = field(default_factory=dict)
    constraints: List[Dict[str, object]] = field(default_factory=list)
    metadata: Dict[str, object] = field(default_factory=dict)

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WorldGenerationParams:
    """Parameters for procedural world generation."""

    name: str
    description: str
    continent_count: int = 3
    climate: str = "temperate"  # temperate, tropical, arid, polar, mixed
    government_type: str = "feudal"  # feudal, tribal, magocratic, merchant, theocratic, warlord
    tech_level: str = "medieval"  # stone age, bronze age, iron age, medieval, renaissance
    magic_level: str = "moderate"  # none, low, moderate, high, wild
    racial_composition: str = "mixed"  # human, elven, dwarven, mixed, custom
    size_modifier: float = 1.0  # 0.5 to 3.0 - scales world size
    complexity_modifier: float = 1.0  # 0.5 to 3.0 - scales number of entities
    atmosphere: str = "neutral"  # neutral, tense, peaceful, apocalyptic, utopian
    danger_level: str = "moderate"  # low, moderate, high, extreme

    def __post_init__(self) -> None:
        """Validate parameters after initialization."""
        # Ensure size and complexity modifiers are within reasonable bounds
        self.size_modifier = max(0.5, min(3.0, self.size_modifier))
        self.complexity_modifier = max(0.5, min(3.0, self.complexity_modifier))

    def get_empire_count(self) -> int:
        """Calculate number of empires based on continent count and complexity."""
        base = max(1, self.continent_count // 2)
        return max(1, int(base * self.complexity_modifier))

    def get_settlement_per_region(self) -> int:
        """Calculate settlements per region based on complexity."""
        base = 3
        return max(1, int(base * self.complexity_modifier))

    def get_npc_per_settlement_modifier(self) -> float:
        """Get population modifier for NPC generation."""
        return self.complexity_modifier
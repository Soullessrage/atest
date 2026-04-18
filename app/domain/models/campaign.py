"""Domain models for D&D campaign management."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from app.domain.models.entity import Entity


# Enums
class CharacterClass(str, Enum):
    """D&D character classes."""

    BARBARIAN = "barbarian"
    BARD = "bard"
    CLERIC = "cleric"
    DRUID = "druid"
    FIGHTER = "fighter"
    MONK = "monk"
    PALADIN = "paladin"
    RANGER = "ranger"
    ROGUE = "rogue"
    SORCERER = "sorcerer"
    WARLOCK = "warlock"
    WIZARD = "wizard"


class EncounterType(str, Enum):
    """Types of encounters."""

    COMBAT = "combat"
    SOCIAL = "social"
    EXPLORATION = "exploration"
    ENVIRONMENTAL = "environmental"


class QuestStatus(str, Enum):
    """Quest status states."""

    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


# Data classes for nested structures
@dataclass
class CampaignSettings:
    """Campaign settings and configuration."""

    difficulty: str = "Medium"  # Easy, Medium, Hard, Deadly
    house_rules: List[str] = field(default_factory=list)
    custom_settings: dict = field(default_factory=dict)


@dataclass
class PartyState:
    """Current state of a party."""

    location: str = "Unknown"
    gold: int = 0
    experience: int = 0


# Campaign entities - these follow the database schema directly
@dataclass
class Campaign(Entity):
    """A D&D campaign tied to a specific world."""

    world_id: str = ""
    game_master_name: Optional[str] = None
    current_date: Optional[str] = None
    session_count: int = 0
    notes: str = ""
    party_id: Optional[str] = None


@dataclass
class Party(Entity):
    """A player party within a campaign."""

    campaign_id: str = ""
    world_id: str = ""
    current_settlement_id: Optional[str] = None
    character_ids: List[str] = field(default_factory=list)
    party_gold: int = 0
    party_inventory: List[str] = field(default_factory=list)
    founded_date: Optional[str] = None


@dataclass
class Character(Entity):
    """A player character in the campaign."""

    campaign_id: str = ""
    party_id: str = ""
    player_name: Optional[str] = None
    character_class: str = ""
    race: str = ""
    background: str = ""
    level: int = 1
    experience: int = 0
    hit_points: int = 10
    max_hit_points: int = 10
    armor_class: int = 10
    alignment: str = "Neutral"
    personality_traits: str = ""
    ideals: str = ""
    bonds: str = ""
    flaws: str = ""
    ability_scores: dict = field(
        default_factory=lambda: {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
        }
    )
    skills: List[str] = field(default_factory=list)
    proficiencies: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    spells: List[str] = field(default_factory=list)
    feats: List[str] = field(default_factory=list)
    backstory: str = ""
    current_location: Optional[str] = None
    gold: int = 0
    status: str = "alive"


@dataclass
class Encounter:
    """An encounter (combat, social, environmental) within the campaign."""

    id: str = ""
    campaign_id: str = ""
    world_id: str = ""
    party_id: str = ""
    encounter_type: str = "combat"
    location: Optional[str] = None
    difficulty: str = "medium"
    enemies: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    reward_xp: int = 0
    reward_gold: int = 0
    completed: bool = False
    created_at: str = ""
    updated_at: str = ""
    locked: bool = False
    metadata: dict = field(default_factory=dict)


@dataclass
class Quest:
    """A quest/objective for the party."""

    id: str = ""
    campaign_id: str = ""
    party_id: str = ""
    giver_npc_id: Optional[str] = None
    title: str = ""
    description: str = ""
    objectives: List[str] = field(default_factory=list)
    reward_xp: int = 0
    reward_gold: int = 0
    reward_items: List[str] = field(default_factory=list)
    status: str = "available"
    difficulty: str = "medium"
    created_at: str = ""
    updated_at: str = ""
    locked: bool = False
    metadata: dict = field(default_factory=dict)


@dataclass
class JournalEntry:
    """Campaign journal entry (log of events)."""

    id: str = ""
    campaign_id: str = ""
    session_date: str = ""
    session_number: int = 0
    content: str = ""
    party_location: Optional[str] = None
    events: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""
    locked: bool = False
    metadata: dict = field(default_factory=dict)


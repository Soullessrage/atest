import sqlite3
from pathlib import Path
from typing import Optional


DEFAULT_SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS worlds (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    continents TEXT DEFAULT '[]',
    empires TEXT DEFAULT '[]',
    kingdoms TEXT DEFAULT '[]',
    regions TEXT DEFAULT '[]',
    settlements TEXT DEFAULT '[]',
    npc_ids TEXT DEFAULT '[]',
    event_ids TEXT DEFAULT '[]',
    rule_set_id TEXT
);

CREATE TABLE IF NOT EXISTS continents (
    id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    empire_ids TEXT DEFAULT '[]',
    kingdom_ids TEXT DEFAULT '[]',
    region_ids TEXT DEFAULT '[]',
    settlement_ids TEXT DEFAULT '[]',
    FOREIGN KEY(world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS empires (
    id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL,
    continent_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    ruler_name TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    kingdom_ids TEXT DEFAULT '[]',
    FOREIGN KEY(world_id) REFERENCES worlds(id) ON DELETE CASCADE,
    FOREIGN KEY(continent_id) REFERENCES continents(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS kingdoms (
    id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL,
    continent_id TEXT,
    empire_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    capital_settlement_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    region_ids TEXT DEFAULT '[]',
    FOREIGN KEY(world_id) REFERENCES worlds(id) ON DELETE CASCADE,
    FOREIGN KEY(continent_id) REFERENCES continents(id) ON DELETE SET NULL,
    FOREIGN KEY(empire_id) REFERENCES empires(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS regions (
    id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL,
    continent_id TEXT,
    empire_id TEXT,
    kingdom_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    settlement_ids TEXT DEFAULT '[]',
    point_of_interest_ids TEXT DEFAULT '[]',
    FOREIGN KEY(world_id) REFERENCES worlds(id) ON DELETE CASCADE,
    FOREIGN KEY(continent_id) REFERENCES continents(id) ON DELETE SET NULL,
    FOREIGN KEY(empire_id) REFERENCES empires(id) ON DELETE SET NULL,
    FOREIGN KEY(kingdom_id) REFERENCES kingdoms(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS settlement_nodes (
    id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL,
    continent_id TEXT,
    empire_id TEXT,
    kingdom_id TEXT,
    region_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    settlement_type TEXT NOT NULL,
    population INTEGER NOT NULL DEFAULT 0,
    location TEXT DEFAULT '{}',
    housing_summary TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    connected_routes TEXT DEFAULT '[]',
    tags TEXT DEFAULT '[]',
    FOREIGN KEY(world_id) REFERENCES worlds(id) ON DELETE CASCADE,
    FOREIGN KEY(continent_id) REFERENCES continents(id) ON DELETE SET NULL,
    FOREIGN KEY(empire_id) REFERENCES empires(id) ON DELETE SET NULL,
    FOREIGN KEY(kingdom_id) REFERENCES kingdoms(id) ON DELETE SET NULL,
    FOREIGN KEY(region_id) REFERENCES regions(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS routes (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    distance REAL NOT NULL DEFAULT 0.0,
    route_type TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY(source_id) REFERENCES settlement_nodes(id) ON DELETE CASCADE,
    FOREIGN KEY(target_id) REFERENCES settlement_nodes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS points_of_interest (
    id TEXT PRIMARY KEY,
    node_id TEXT,
    category TEXT,
    importance INTEGER NOT NULL DEFAULT 1,
    influence_scope TEXT DEFAULT '[]',
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY(node_id) REFERENCES settlement_nodes(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS npcs (
    id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL,
    settlement_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    age INTEGER NOT NULL DEFAULT 0,
    gender TEXT,
    race_id TEXT,
    subrace_id TEXT,
    occupation TEXT,
    social_role TEXT,
    residence_id TEXT,
    wealth_status TEXT,
    personality_traits TEXT DEFAULT '[]',
    goals TEXT DEFAULT '[]',
    motivations TEXT DEFAULT '[]',
    flaws TEXT DEFAULT '[]',
    history TEXT DEFAULT '[]',
    family_ids TEXT DEFAULT '[]',
    relationship_ids TEXT DEFAULT '[]',
    tags TEXT DEFAULT '[]',
    health_status TEXT,
    injuries TEXT DEFAULT '[]',
    illnesses TEXT DEFAULT '[]',
    fertility_score REAL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY(world_id) REFERENCES worlds(id) ON DELETE CASCADE,
    FOREIGN KEY(settlement_id) REFERENCES settlement_nodes(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS relationships (
    id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    weight REAL NOT NULL DEFAULT 0.0,
    history TEXT DEFAULT '[]',
    tags TEXT DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY(world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS races (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    cultural_tags TEXT DEFAULT '[]',
    lifespan INTEGER,
    preferred_occupations TEXT DEFAULT '[]',
    settlement_preferences TEXT DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS event_definitions (
    id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    scope TEXT NOT NULL,
    category TEXT,
    probability REAL NOT NULL DEFAULT 0.0,
    duration_days INTEGER NOT NULL DEFAULT 0,
    conditions TEXT DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY(world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS event_instances (
    id TEXT PRIMARY KEY,
    definition_id TEXT NOT NULL,
    world_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    affected_scope TEXT,
    effect_summary TEXT,
    details TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY(definition_id) REFERENCES event_definitions(id) ON DELETE CASCADE,
    FOREIGN KEY(world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS campaigns (
    id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    game_master_name TEXT,
    current_date TEXT,
    session_count INTEGER NOT NULL DEFAULT 0,
    notes TEXT DEFAULT '',
    party_id TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    difficulty_level TEXT DEFAULT 'medium',
    house_rules TEXT DEFAULT '[]',
    custom_settings TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY(world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS parties (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    world_id TEXT NOT NULL,
    name TEXT,
    description TEXT,
    current_settlement_id TEXT,
    character_ids TEXT DEFAULT '[]',
    party_gold INTEGER NOT NULL DEFAULT 0,
    party_inventory TEXT DEFAULT '[]',
    founded_date TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY(world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS characters (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    party_id TEXT NOT NULL,
    player_name TEXT,
    name TEXT NOT NULL,
    description TEXT,
    character_class TEXT,
    race TEXT,
    background TEXT,
    level INTEGER NOT NULL DEFAULT 1,
    experience INTEGER NOT NULL DEFAULT 0,
    hit_points INTEGER NOT NULL DEFAULT 10,
    max_hit_points INTEGER NOT NULL DEFAULT 10,
    armor_class INTEGER NOT NULL DEFAULT 10,
    alignment TEXT DEFAULT 'Neutral',
    personality_traits TEXT DEFAULT '',
    ideals TEXT DEFAULT '',
    bonds TEXT DEFAULT '',
    flaws TEXT DEFAULT '',
    ability_scores TEXT DEFAULT '{}',
    skills TEXT DEFAULT '[]',
    proficiencies TEXT DEFAULT '[]',
    equipment TEXT DEFAULT '[]',
    spells TEXT DEFAULT '[]',
    feats TEXT DEFAULT '[]',
    backstory TEXT DEFAULT '',
    current_location TEXT,
    gold INTEGER NOT NULL DEFAULT 0,
    status TEXT DEFAULT 'alive',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY(party_id) REFERENCES parties(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS encounters (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    world_id TEXT NOT NULL,
    party_id TEXT NOT NULL,
    encounter_type TEXT DEFAULT 'combat',
    location TEXT,
    difficulty TEXT DEFAULT 'medium',
    enemies TEXT DEFAULT '[]',
    objectives TEXT DEFAULT '[]',
    reward_xp INTEGER NOT NULL DEFAULT 0,
    reward_gold INTEGER NOT NULL DEFAULT 0,
    completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY(world_id) REFERENCES worlds(id) ON DELETE CASCADE,
    FOREIGN KEY(party_id) REFERENCES parties(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quests (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    party_id TEXT NOT NULL,
    giver_npc_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    objectives TEXT DEFAULT '[]',
    reward_xp INTEGER NOT NULL DEFAULT 0,
    reward_gold INTEGER NOT NULL DEFAULT 0,
    reward_items TEXT DEFAULT '[]',
    status TEXT DEFAULT 'available',
    difficulty TEXT DEFAULT 'medium',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY(party_id) REFERENCES parties(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    session_date TEXT NOT NULL,
    session_number INTEGER NOT NULL DEFAULT 0,
    content TEXT DEFAULT '',
    party_location TEXT,
    events TEXT DEFAULT '[]',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    locked INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);
"""


def initialize_database(path: Path, schema_sql: Optional[str] = None) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    sql = schema_sql or DEFAULT_SCHEMA_SQL
    conn.executescript(sql)
    conn.commit()
    return conn

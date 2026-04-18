"""Tests for Phase 7: Campaign Management & Player Integration."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from app.core.services.campaign_service import CampaignService
from app.data.repositories.campaign_repository import (
    CampaignRepository,
    PartyRepository,
    CharacterRepository,
    EncounterRepository,
    QuestRepository,
    JournalEntryRepository,
)
from app.data.sqlite.database import initialize_database


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database for testing."""
    return tmp_path / "test_campaign.db"


@pytest.fixture
def test_db(temp_db_path):
    """Initialize test database."""
    db = initialize_database(temp_db_path)
    yield db
    db.close()


@pytest.fixture
def test_repositories(test_db):
    """Create repository instances."""
    return {
        "campaign": CampaignRepository(test_db),
        "party": PartyRepository(test_db),
        "character": CharacterRepository(test_db),
        "encounter": EncounterRepository(test_db),
        "quest": QuestRepository(test_db),
        "journal": JournalEntryRepository(test_db),
    }


@pytest.fixture
def campaign_service(test_repositories):
    """Create campaign service with test world."""
    test_db = test_repositories["campaign"].conn
    # Create a test world in the database
    test_db.execute(
        """INSERT INTO worlds (id, name, description, created_at, updated_at, locked, metadata)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("world-1", "Test World", "Test Description", "2024-01-01T00:00:00", "2024-01-01T00:00:00", 0, "{}"),
    )
    test_db.commit()
    
    mock_persistence = MagicMock()
    mock_persistence.get_world.return_value = MagicMock(id="world-1")

    return CampaignService(
        campaign_repo=test_repositories["campaign"],
        party_repo=test_repositories["party"],
        character_repo=test_repositories["character"],
        encounter_repo=test_repositories["encounter"],
        quest_repo=test_repositories["quest"],
        journal_entry_repo=test_repositories["journal"],
        persistence_service=mock_persistence,
    )


class TestCampaignOperations:
    """Test campaign creation and retrieval."""

    def test_create_campaign(self, campaign_service):
        """Test creating a new campaign."""
        campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Dragon's Hoard",
            description="A quest to retrieve the lost dragon hoard",
            difficulty="Hard",
        )

        assert campaign.world_id == "world-1"
        assert campaign.name == "Dragon's Hoard"
        assert campaign.description == "A quest to retrieve the lost dragon hoard"

    def test_get_campaign(self, campaign_service):
        """Test retrieving a campaign."""
        created_campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Lost City",
            description="Explore the lost city",
        )

        retrieved = campaign_service.get_campaign(created_campaign.id)

        assert retrieved is not None
        assert retrieved.id == created_campaign.id
        assert retrieved.name == "Lost City"

    def test_list_campaigns_for_world(self, campaign_service):
        """Test listing campaigns for a specific world."""
        campaign1 = campaign_service.create_campaign(
            world_id="world-1",
            name="Campaign 1",
        )
        campaign2 = campaign_service.create_campaign(
            world_id="world-1",
            name="Campaign 2",
        )

        world_1_campaigns = campaign_service.list_campaigns_for_world("world-1")

        assert len(world_1_campaigns) >= 2


class TestPartyOperations:
    """Test party creation and management."""

    def test_create_party(self, campaign_service):
        """Test creating a party."""
        campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Test Campaign",
        )

        party = campaign_service.create_party(
            campaign_id=campaign.id,
            name="The Adventurers",
            description="A brave party of adventurers",
        )

        assert party.campaign_id == campaign.id
        assert party.name == "The Adventurers"
        assert len(party.character_ids) == 0
        assert party.party_gold == 0

    def test_add_character_to_party(self, campaign_service):
        """Test adding a character to a party."""
        campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Test Campaign",
        )
        party = campaign_service.create_party(
            campaign_id=campaign.id,
            name="Test Party",
        )

        character = campaign_service.create_character(
            party_id=party.id,
            name="Aragorn",
            char_class="Ranger",
            level=5,
            race="Human",
        )

        updated_party = campaign_service.get_party(party.id)

        assert character.id in updated_party.character_ids

    def test_update_party_gold(self, campaign_service):
        """Test updating party gold."""
        campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Test Campaign",
        )
        party = campaign_service.create_party(
            campaign_id=campaign.id,
            name="Test Party",
        )

        party = campaign_service.update_party_gold(party.id, 500)
        assert party.party_gold == 500


class TestCharacterOperations:
    """Test character creation and management."""

    def test_create_character(self, campaign_service):
        """Test creating a character."""
        campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Test Campaign",
        )
        party = campaign_service.create_party(
            campaign_id=campaign.id,
            name="Test Party",
        )

        character = campaign_service.create_character(
            party_id=party.id,
            name="Frodo",
            char_class="Rogue",
            level=2,
            race="Halfling",
        )

        assert character.party_id == party.id
        assert character.name == "Frodo"
        assert character.race == "Halfling"
        assert character.level == 2

    def test_list_party_members(self, campaign_service):
        """Test listing party members."""
        campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Test Campaign",
        )
        party = campaign_service.create_party(
            campaign_id=campaign.id,
            name="Test Party",
        )

        char1 = campaign_service.create_character(
            party_id=party.id,
            name="Character 1",
            char_class="Fighter",
        )
        char2 = campaign_service.create_character(
            party_id=party.id,
            name="Character 2",
            char_class="Cleric",
        )

        members = campaign_service.list_party_members(party.id)

        assert len(members) >= 2

    def test_add_character_experience(self, campaign_service):
        """Test adding experience to character."""
        campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Test Campaign",
        )
        party = campaign_service.create_party(
            campaign_id=campaign.id,
            name="Test Party",
        )

        character = campaign_service.create_character(
            party_id=party.id,
            name="Legolas",
            char_class="Ranger",
        )

        assert character.experience == 0

        character = campaign_service.add_character_experience(character.id, 500)
        assert character.experience == 500


class TestQuestOperations:
    """Test quest creation and management."""

    def test_create_quest(self, campaign_service):
        """Test creating a quest."""
        campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Test Campaign",
        )
        party = campaign_service.create_party(
            campaign_id=campaign.id,
            name="Test Party",
        )

        quest = campaign_service.create_quest(
            campaign_id=campaign.id,
            title="Recover the Amulet",
            description="Find the ancient amulet",
            objectives=["Explore the dungeon", "Defeat the guardian", "Return with amulet"],
            reward_xp=1000,
            reward_gold=500,
        )

        assert quest.campaign_id == campaign.id
        assert quest.title == "Recover the Amulet"
        assert len(quest.objectives) == 3
        assert quest.status == "available"

    def test_quest_lifecycle(self, campaign_service):
        """Test quest status transitions."""
        campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Test Campaign",
        )
        party = campaign_service.create_party(
            campaign_id=campaign.id,
            name="Test Party",
        )

        quest = campaign_service.create_quest(
            campaign_id=campaign.id,
            title="Test Quest",
        )

        assert quest.status == "available"

        quest = campaign_service.accept_quest(quest.id)
        assert quest.status == "active"

        quest = campaign_service.complete_quest(quest.id)
        assert quest.status == "completed"

    def test_list_active_quests(self, campaign_service):
        """Test listing active quests."""
        campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Test Campaign",
        )
        party = campaign_service.create_party(
            campaign_id=campaign.id,
            name="Test Party",
        )

        quest1 = campaign_service.create_quest(
            campaign_id=campaign.id,
            title="Quest 1",
        )
        quest2 = campaign_service.create_quest(
            campaign_id=campaign.id,
            title="Quest 2",
        )

        campaign_service.accept_quest(quest1.id)
        campaign_service.accept_quest(quest2.id)

        active_quests = campaign_service.list_active_quests(campaign.id)

        assert len(active_quests) >= 2


class TestEncounterOperations:
    """Test encounter creation and management."""

    def test_create_encounter(self, campaign_service):
        """Test creating an encounter."""
        campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Test Campaign",
        )
        party = campaign_service.create_party(
            campaign_id=campaign.id,
            name="Test Party",
        )

        encounter = campaign_service.create_encounter(
            campaign_id=campaign.id,
            name="Goblin Ambush",
            encounter_type="combat",
            difficulty="Medium",
            description="A band of goblins attacks!",
        )

        assert encounter.campaign_id == campaign.id
        assert encounter.location == "Goblin Ambush"


class TestJournalOperations:
    """Test session journal management."""

    def test_record_session(self, campaign_service):
        """Test recording a session."""
        campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Test Campaign",
        )

        entry = campaign_service.record_session(
            campaign_id=campaign.id,
            session_number=1,
            summary="The party met in the tavern and received their first quest",
            notes="Good start",
        )

        assert entry.campaign_id == campaign.id
        assert entry.session_number == 1

    def test_list_campaign_journal(self, campaign_service):
        """Test listing journal entries."""
        campaign = campaign_service.create_campaign(
            world_id="world-1",
            name="Test Campaign",
        )

        entry1 = campaign_service.record_session(
            campaign_id=campaign.id,
            session_number=1,
            summary="Session 1",
        )
        entry2 = campaign_service.record_session(
            campaign_id=campaign.id,
            session_number=2,
            summary="Session 2",
        )

        entries = campaign_service.list_campaign_journal(campaign.id)

        assert len(entries) >= 2

"""Campaign management service for D&D campaign administration."""
from uuid import uuid4
from datetime import datetime

from app.domain.models.campaign import (
    Campaign,
    Party,
    Character,
    Encounter,
    Quest,
    JournalEntry,
)
from app.data.repositories.campaign_repository import (
    CampaignRepository,
    PartyRepository,
    CharacterRepository,
    EncounterRepository,
    QuestRepository,
    JournalEntryRepository,
)
from app.core.services.persistence_service import PersistenceService


class CampaignService:
    """Service for managing campaigns, parties, and related entities."""

    def __init__(
        self,
        campaign_repo: CampaignRepository,
        party_repo: PartyRepository,
        character_repo: CharacterRepository,
        encounter_repo: EncounterRepository,
        quest_repo: QuestRepository,
        journal_entry_repo: JournalEntryRepository,
        persistence_service: PersistenceService,
    ):
        self.campaign_repo = campaign_repo
        self.party_repo = party_repo
        self.character_repo = character_repo
        self.encounter_repo = encounter_repo
        self.quest_repo = quest_repo
        self.journal_entry_repo = journal_entry_repo
        self.persistence_service = persistence_service

    # Campaign operations
    def create_campaign(
        self,
        world_id: str,
        name: str,
        description: str = "",
        difficulty: str = "Medium",
    ) -> Campaign:
        """Create a new campaign for a world."""
        campaign = Campaign(
            id=str(uuid4()),
            name=name,
            description=description,
            world_id=world_id,
            party_id=None,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        self.campaign_repo.add(campaign)
        return campaign

    def get_campaign(self, campaign_id: str) -> Campaign | None:
        """Retrieve a campaign by ID."""
        return self.campaign_repo.get(campaign_id)

    def list_campaigns_for_world(self, world_id: str) -> list[Campaign]:
        """List all campaigns for a world."""
        return self.campaign_repo.list_by_world(world_id)

    def list_active_campaigns(self) -> list[Campaign]:
        """List all active campaigns."""
        return self.campaign_repo.list_active()

    def update_campaign(self, campaign: Campaign) -> Campaign:
        """Update campaign details."""
        campaign.updated_at = datetime.now().isoformat()
        self.campaign_repo.update(campaign)
        return campaign

    # Party operations
    def create_party(
        self,
        campaign_id: str,
        name: str,
        description: str = "",
    ) -> Party:
        """Create a new party for a campaign."""
        campaign = self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        party = Party(
            id=str(uuid4()),
            campaign_id=campaign_id,
            world_id=campaign.world_id,
            name=name,
            description=description,
            character_ids=[],
            party_gold=0,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        self.party_repo.add(party)

        # Link party to campaign
        campaign.party_id = party.id
        self.campaign_repo.update(campaign)

        return party

    def get_party(self, party_id: str) -> Party | None:
        """Retrieve a party by ID."""
        return self.party_repo.get(party_id)

    def add_character_to_party(self, party_id: str, character_id: str) -> Party:
        """Add a character to a party."""
        party = self.party_repo.get(party_id)
        if party and character_id not in party.character_ids:
            party.character_ids.append(character_id)
            party.updated_at = datetime.now().isoformat()
            self.party_repo.update(party)
        return party

    def remove_character_from_party(self, party_id: str, character_id: str) -> Party:
        """Remove a character from a party."""
        party = self.party_repo.get(party_id)
        if party and character_id in party.character_ids:
            party.character_ids.remove(character_id)
            party.updated_at = datetime.now().isoformat()
            self.party_repo.update(party)
        return party

    def update_party_location(self, party_id: str, location: str) -> Party:
        """Update party's current location."""
        party = self.party_repo.get(party_id)
        if party:
            party.current_settlement_id = location
            party.updated_at = datetime.now().isoformat()
            self.party_repo.update(party)
        return party

    def update_party_gold(self, party_id: str, gold_delta: int) -> Party:
        """Adjust party's gold amount."""
        party = self.party_repo.get(party_id)
        if party:
            party.party_gold = max(0, party.party_gold + gold_delta)
            party.updated_at = datetime.now().isoformat()
            self.party_repo.update(party)
        return party

    # Character operations
    def create_character(
        self,
        party_id: str,
        name: str,
        char_class: str,
        level: int = 1,
        race: str = "Human",
    ) -> Character:
        """Create a new character for a party."""
        party = self.party_repo.get(party_id)
        if not party:
            raise ValueError(f"Party {party_id} not found")

        character = Character(
            id=str(uuid4()),
            campaign_id=party.campaign_id,
            party_id=party_id,
            name=name,
            race=race,
            character_class=char_class,
            level=level,
            experience=0,
            ability_scores={
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10,
            },
            skills=[],
            hit_points=10,
            armor_class=10,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        self.character_repo.add(character)
        # Add character to party
        self.add_character_to_party(party_id, character.id)
        return character

    def get_character(self, character_id: str) -> Character | None:
        """Retrieve a character by ID."""
        return self.character_repo.get(character_id)

    def list_party_members(self, party_id: str) -> list[Character]:
        """List all characters in a party."""
        return self.character_repo.list_by_party(party_id)

    def update_character(self, character: Character) -> Character:
        """Update character details."""
        character.updated_at = datetime.now().isoformat()
        self.character_repo.update(character)
        return character

    def add_character_experience(
        self, character_id: str, experience: int
    ) -> Character:
        """Add experience to a character."""
        character = self.character_repo.get(character_id)
        if character:
            character.experience += experience
            character.updated_at = datetime.now().isoformat()
            self.character_repo.update(character)
        return character

    # Encounter operations
    def create_encounter(
        self,
        campaign_id: str,
        name: str,
        encounter_type: str,
        difficulty: str = "medium",
        description: str = "",
    ) -> Encounter:
        """Create a new encounter."""
        campaign = self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        encounter = Encounter(
            id=str(uuid4()),
            campaign_id=campaign_id,
            world_id=campaign.world_id,
            party_id=campaign.party_id or "",
            encounter_type=encounter_type,
            location=name,
            difficulty=difficulty,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        self.encounter_repo.add(encounter)
        return encounter

    def get_encounter(self, encounter_id: str) -> Encounter | None:
        """Retrieve an encounter by ID."""
        return self.encounter_repo.get(encounter_id)

    def list_campaign_encounters(self, campaign_id: str) -> list[Encounter]:
        """List all encounters in a campaign."""
        return self.encounter_repo.list_by_campaign(campaign_id)

    def resolve_encounter(self, encounter_id: str, status: str) -> Encounter:
        """Mark an encounter as resolved."""
        encounter = self.encounter_repo.get(encounter_id)
        if encounter:
            encounter.completed = status == "success"
            encounter.updated_at = datetime.now().isoformat()
            self.encounter_repo.update(encounter)
        return encounter

    # Quest operations
    def create_quest(
        self,
        campaign_id: str,
        title: str,
        description: str = "",
        objectives: list[str] | None = None,
        reward_xp: int = 0,
        reward_gold: int = 0,
    ) -> Quest:
        """Create a new quest."""
        campaign = self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        quest = Quest(
            id=str(uuid4()),
            campaign_id=campaign_id,
            party_id=campaign.party_id or "",
            title=title,
            description=description,
            objectives=objectives or [],
            status="available",
            reward_xp=reward_xp,
            reward_gold=reward_gold,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        self.quest_repo.add(quest)
        return quest

    def get_quest(self, quest_id: str) -> Quest | None:
        """Retrieve a quest by ID."""
        return self.quest_repo.get(quest_id)

    def list_campaign_quests(self, campaign_id: str) -> list[Quest]:
        """List all quests in a campaign."""
        return self.quest_repo.list_by_campaign(campaign_id)

    def list_active_quests(self, campaign_id: str) -> list[Quest]:
        """List active quests in a campaign."""
        all_quests = self.quest_repo.list_by_campaign(campaign_id)
        return [q for q in all_quests if q.status in ["available", "active"]]

    def accept_quest(self, quest_id: str) -> Quest:
        """Accept a quest (change status to active)."""
        quest = self.quest_repo.get(quest_id)
        if quest and quest.status == "available":
            quest.status = "active"
            quest.updated_at = datetime.now().isoformat()
            self.quest_repo.update(quest)
        return quest

    def complete_quest(self, quest_id: str) -> Quest:
        """Complete a quest."""
        quest = self.quest_repo.get(quest_id)
        if quest and quest.status == "active":
            quest.status = "completed"
            quest.updated_at = datetime.now().isoformat()
            self.quest_repo.update(quest)
        return quest

    def abandon_quest(self, quest_id: str) -> Quest:
        """Abandon a quest."""
        quest = self.quest_repo.get(quest_id)
        if quest and quest.status == "active":
            quest.status = "abandoned"
            quest.updated_at = datetime.now().isoformat()
            self.quest_repo.update(quest)
        return quest

    # Journal operations
    def record_session(
        self,
        campaign_id: str,
        session_number: int,
        summary: str,
        notes: str = "",
    ) -> JournalEntry:
        """Record a session journal entry."""
        entry = JournalEntry(
            id=str(uuid4()),
            campaign_id=campaign_id,
            session_number=session_number,
            session_date=datetime.now().isoformat(),
            content=summary,
            notes=notes,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        self.journal_entry_repo.add(entry)
        return entry

    def get_journal_entry(self, entry_id: str) -> JournalEntry | None:
        """Retrieve a journal entry by ID."""
        return self.journal_entry_repo.get(entry_id)

    def list_campaign_journal(self, campaign_id: str) -> list[JournalEntry]:
        """List all journal entries for a campaign."""
        return self.journal_entry_repo.list_by_campaign(campaign_id)

    def get_latest_session(self, campaign_id: str) -> JournalEntry | None:
        """Get the latest session journal entry."""
        entries = self.journal_entry_repo.list_by_campaign(campaign_id)
        if entries:
            return entries[0]  # Already sorted by session_number DESC
        return None

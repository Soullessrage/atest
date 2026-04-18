"""ViewModel for campaign management UI."""
from PySide6.QtCore import QObject, Signal, Slot

from app.core.services.campaign_service import CampaignService
from app.core.services.persistence_service import PersistenceService
from app.domain.models.campaign import (
    Campaign,
    Party,
    Character,
    Encounter,
    Quest,
    JournalEntry,
    CharacterClass,
    EncounterType,
)


class CampaignViewModel(QObject):
    """ViewModel for campaign management with reactive signals."""

    # Campaign signals
    campaigns_loaded = Signal(list)
    campaign_selected = Signal(object)
    campaign_created = Signal(object)
    campaign_updated = Signal(object)

    # Party signals
    party_created = Signal(object)
    party_updated = Signal(object)
    party_members_loaded = Signal(list)

    # Character signals
    character_created = Signal(object)
    character_updated = Signal(object)
    character_deleted = Signal(str)
    character_list_updated = Signal(list)

    # Quest signals
    quests_loaded = Signal(list)
    active_quests_loaded = Signal(list)
    quest_status_changed = Signal(str, str)

    # Encounter signals
    encounters_loaded = Signal(list)
    encounter_created = Signal(object)
    encounter_resolved = Signal(str, str)

    # Journal signals
    journal_loaded = Signal(list)
    session_recorded = Signal(object)

    # Error handling
    error_occurred = Signal(str)

    def __init__(
        self,
        campaign_service: CampaignService,
        persistence_service: PersistenceService,
    ):
        super().__init__()
        self.campaign_service = campaign_service
        self.persistence_service = persistence_service
        self.selected_campaign: Campaign | None = None
        self.selected_party: Party | None = None
        self.selected_character: Character | None = None

    # Campaign operations
    @Slot()
    def load_all_campaigns(self) -> None:
        """Load all active campaigns."""
        try:
            campaigns = self.campaign_service.list_active_campaigns()
            self.campaigns_loaded.emit(campaigns)
        except Exception as e:
            self.error_occurred.emit(f"Failed to load campaigns: {str(e)}")

    @Slot(str)
    def load_world_campaigns(self, world_id: str) -> None:
        """Load all campaigns for a specific world."""
        try:
            campaigns = self.campaign_service.list_campaigns_for_world(world_id)
            self.campaigns_loaded.emit(campaigns)
        except Exception as e:
            self.error_occurred.emit(f"Failed to load world campaigns: {str(e)}")

    @Slot(str, str, str, str)
    def create_campaign(
        self, world_id: str, name: str, description: str, difficulty: str
    ) -> None:
        """Create a new campaign."""
        try:
            # Verify world exists
            if not self.persistence_service.get_world(world_id):
                self.error_occurred.emit(f"World {world_id} not found")
                return

            campaign = self.campaign_service.create_campaign(
                world_id=world_id,
                name=name,
                description=description,
                difficulty=difficulty,
            )
            self.campaign_created.emit(campaign)
            self.selected_campaign = campaign
            self.campaign_selected.emit(campaign)
        except Exception as e:
            self.error_occurred.emit(f"Failed to create campaign: {str(e)}")

    @Slot(str)
    def select_campaign(self, campaign_id: str) -> None:
        """Select a campaign for editing."""
        try:
            campaign = self.campaign_service.get_campaign(campaign_id)
            if campaign:
                self.selected_campaign = campaign
                self.campaign_selected.emit(campaign)
                # Load associated party if exists
                if campaign.party_id:
                    party = self.campaign_service.get_party(campaign.party_id)
                    if party:
                        self.selected_party = party
            else:
                self.error_occurred.emit(f"Campaign {campaign_id} not found")
        except Exception as e:
            self.error_occurred.emit(f"Failed to select campaign: {str(e)}")

    # Party operations
    @Slot(str, str, str)
    def create_party(self, campaign_id: str, name: str, description: str) -> None:
        """Create a new party for the campaign."""
        try:
            if not self.selected_campaign or self.selected_campaign.id != campaign_id:
                self.error_occurred.emit("No campaign selected")
                return

            party = self.campaign_service.create_party(
                campaign_id=campaign_id,
                name=name,
                description=description,
            )
            self.selected_party = party
            self.party_created.emit(party)
            # Update campaign with party
            self.selected_campaign.party_id = party.id
            self.campaign_updated.emit(self.selected_campaign)
        except Exception as e:
            self.error_occurred.emit(f"Failed to create party: {str(e)}")

    @Slot()
    def load_party_members(self) -> None:
        """Load all characters in the selected party."""
        try:
            if not self.selected_party:
                self.error_occurred.emit("No party selected")
                return

            characters = self.campaign_service.list_party_members(
                self.selected_party.id
            )
            self.party_members_loaded.emit(characters)
        except Exception as e:
            self.error_occurred.emit(f"Failed to load party members: {str(e)}")

    @Slot(str, int)
    def update_party_gold(self, party_id: str, amount: int) -> None:
        """Update party's gold."""
        try:
            party = self.campaign_service.update_party_gold(party_id, amount)
            if self.selected_party and self.selected_party.id == party_id:
                self.selected_party = party
            self.party_updated.emit(party)
        except Exception as e:
            self.error_occurred.emit(f"Failed to update party gold: {str(e)}")

    @Slot(str, str)
    def update_party_location(self, party_id: str, location: str) -> None:
        """Update party's location."""
        try:
            party = self.campaign_service.update_party_location(party_id, location)
            if self.selected_party and self.selected_party.id == party_id:
                self.selected_party = party
            self.party_updated.emit(party)
        except Exception as e:
            self.error_occurred.emit(f"Failed to update party location: {str(e)}")

    # Character operations
    @Slot(str, str, str, int, str)
    def create_character(
        self,
        party_id: str,
        name: str,
        char_class: str,
        level: int,
        race: str,
    ) -> None:
        """Create a new character."""
        try:
            if not self.selected_party or self.selected_party.id != party_id:
                self.error_occurred.emit("No party selected")
                return

            character = self.campaign_service.create_character(
                party_id=party_id,
                name=name,
                char_class=char_class,
                level=level,
                race=race,
            )
            self.character_created.emit(character)

            # Reload party members
            self.load_party_members()
        except Exception as e:
            self.error_occurred.emit(f"Failed to create character: {str(e)}")

    @Slot(str)
    def select_character(self, character_id: str) -> None:
        """Select a character for editing."""
        try:
            character = self.campaign_service.get_character(character_id)
            if character:
                self.selected_character = character
            else:
                self.error_occurred.emit(f"Character {character_id} not found")
        except Exception as e:
            self.error_occurred.emit(f"Failed to select character: {str(e)}")

    @Slot(str, int)
    def add_character_experience(self, character_id: str, experience: int) -> None:
        """Award experience to a character."""
        try:
            character = self.campaign_service.add_character_experience(
                character_id, experience
            )
            if self.selected_character and self.selected_character.id == character_id:
                self.selected_character = character
            self.character_updated.emit(character)
        except Exception as e:
            self.error_occurred.emit(f"Failed to add experience: {str(e)}")

    # Quest operations
    @Slot()
    def load_campaign_quests(self) -> None:
        """Load all quests for the selected campaign."""
        try:
            if not self.selected_campaign:
                self.error_occurred.emit("No campaign selected")
                return

            quests = self.campaign_service.list_campaign_quests(
                self.selected_campaign.id
            )
            self.quests_loaded.emit(quests)

            # Also emit active quests
            active_quests = self.campaign_service.list_active_quests(
                self.selected_campaign.id
            )
            self.active_quests_loaded.emit(active_quests)
        except Exception as e:
            self.error_occurred.emit(f"Failed to load quests: {str(e)}")

    @Slot(str, str, str, list, int, int)
    def create_quest(
        self,
        campaign_id: str,
        title: str,
        description: str,
        objectives: list[str],
        reward_experience: int,
        reward_gold: int,
    ) -> None:
        """Create a new quest."""
        try:
            if not self.selected_campaign or self.selected_campaign.id != campaign_id:
                self.error_occurred.emit("No campaign selected")
                return

            quest = self.campaign_service.create_quest(
                campaign_id=campaign_id,
                title=title,
                description=description,
                objectives=objectives,
                reward_experience=reward_experience,
                reward_gold=reward_gold,
            )

            # Reload quests
            self.load_campaign_quests()
        except Exception as e:
            self.error_occurred.emit(f"Failed to create quest: {str(e)}")

    @Slot(str)
    def accept_quest(self, quest_id: str) -> None:
        """Accept a quest."""
        try:
            quest = self.campaign_service.accept_quest(quest_id)
            self.quest_status_changed.emit(quest_id, quest.status.value)
            self.load_campaign_quests()
        except Exception as e:
            self.error_occurred.emit(f"Failed to accept quest: {str(e)}")

    @Slot(str)
    def complete_quest(self, quest_id: str) -> None:
        """Complete a quest."""
        try:
            quest = self.campaign_service.complete_quest(quest_id)
            self.quest_status_changed.emit(quest_id, quest.status.value)
            self.load_campaign_quests()
        except Exception as e:
            self.error_occurred.emit(f"Failed to complete quest: {str(e)}")

    @Slot(str)
    def abandon_quest(self, quest_id: str) -> None:
        """Abandon a quest."""
        try:
            quest = self.campaign_service.abandon_quest(quest_id)
            self.quest_status_changed.emit(quest_id, quest.status.value)
            self.load_campaign_quests()
        except Exception as e:
            self.error_occurred.emit(f"Failed to abandon quest: {str(e)}")

    # Encounter operations
    @Slot()
    def load_campaign_encounters(self) -> None:
        """Load all encounters for the selected campaign."""
        try:
            if not self.selected_campaign:
                self.error_occurred.emit("No campaign selected")
                return

            encounters = self.campaign_service.list_campaign_encounters(
                self.selected_campaign.id
            )
            self.encounters_loaded.emit(encounters)
        except Exception as e:
            self.error_occurred.emit(f"Failed to load encounters: {str(e)}")

    @Slot(str, str, str, str, str)
    def create_encounter(
        self,
        campaign_id: str,
        name: str,
        encounter_type: str,
        difficulty: str,
        description: str,
    ) -> None:
        """Create a new encounter."""
        try:
            if not self.selected_campaign or self.selected_campaign.id != campaign_id:
                self.error_occurred.emit("No campaign selected")
                return

            encounter = self.campaign_service.create_encounter(
                campaign_id=campaign_id,
                name=name,
                encounter_type=encounter_type,
                difficulty=difficulty,
                description=description,
            )
            self.encounter_created.emit(encounter)
            self.load_campaign_encounters()
        except Exception as e:
            self.error_occurred.emit(f"Failed to create encounter: {str(e)}")

    @Slot(str, str)
    def resolve_encounter(self, encounter_id: str, status: str) -> None:
        """Resolve an encounter."""
        try:
            encounter = self.campaign_service.resolve_encounter(encounter_id, status)
            self.encounter_resolved.emit(encounter_id, status)
            self.load_campaign_encounters()
        except Exception as e:
            self.error_occurred.emit(f"Failed to resolve encounter: {str(e)}")

    # Journal operations
    @Slot()
    def load_campaign_journal(self) -> None:
        """Load all journal entries for the selected campaign."""
        try:
            if not self.selected_campaign:
                self.error_occurred.emit("No campaign selected")
                return

            entries = self.campaign_service.list_campaign_journal(
                self.selected_campaign.id
            )
            self.journal_loaded.emit(entries)
        except Exception as e:
            self.error_occurred.emit(f"Failed to load journal: {str(e)}")

    @Slot(int, str, list)
    def record_session(
        self, session_number: int, summary: str, highlights: list[str]
    ) -> None:
        """Record a session in the campaign journal."""
        try:
            if not self.selected_campaign:
                self.error_occurred.emit("No campaign selected")
                return

            entry = self.campaign_service.record_session(
                campaign_id=self.selected_campaign.id,
                session_number=session_number,
                summary=summary,
                highlights=highlights,
            )
            self.session_recorded.emit(entry)
            self.load_campaign_journal()
        except Exception as e:
            self.error_occurred.emit(f"Failed to record session: {str(e)}")

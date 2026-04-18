"""Party Management page for managing parties and characters."""
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QFormLayout,
    QMessageBox,
    QTabWidget,
)
from PySide6.QtCore import Qt

from app.ui.viewmodels.campaign_viewmodel import CampaignViewModel


class CreatePartyDialog(QDialog):
    """Dialog for creating a new party."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Party")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        layout.addRow("Party Name:", self.name_input)

        self.description_input = QLineEdit()
        layout.addRow("Description:", self.description_input)

        button_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        cancel_btn = QPushButton("Cancel")
        create_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "description": self.description_input.text(),
        }


class CreateCharacterDialog(QDialog):
    """Dialog for creating a new character."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Character")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        layout.addRow("Character Name:", self.name_input)

        self.race_input = QLineEdit()
        self.race_input.setText("Human")
        layout.addRow("Race:", self.race_input)

        self.class_combo = QComboBox()
        self.class_combo.addItems([
            "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk",
            "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
        ])
        layout.addRow("Class:", self.class_combo)

        self.level_spin = QSpinBox()
        self.level_spin.setValue(1)
        self.level_spin.setMinimum(1)
        self.level_spin.setMaximum(20)
        layout.addRow("Level:", self.level_spin)

        button_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        cancel_btn = QPushButton("Cancel")
        create_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "race": self.race_input.text(),
            "char_class": self.class_combo.currentText(),
            "level": self.level_spin.value(),
        }


class PartyManagementPage(QWidget):
    """Party Management for creating and managing parties and characters."""

    def __init__(self, viewmodel: CampaignViewModel):
        super().__init__()
        self.viewmodel = viewmodel
        self.current_party = None
        self.characters = []
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Party Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #654321;")
        layout.addWidget(title)

        # Create party button
        button_layout = QHBoxLayout()
        create_party_btn = QPushButton("+ Create New Party")
        create_party_btn.clicked.connect(self._show_create_party_dialog)
        button_layout.addWidget(create_party_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Tab widget for party selection and character management
        tabs = QTabWidget()

        # Party List Tab
        party_layout = QVBoxLayout()
        self.party_list = QListWidget()
        self.party_list.itemClicked.connect(self._on_party_selected)
        party_layout.addWidget(QLabel("Parties:"))
        party_layout.addWidget(self.party_list)
        party_widget = QWidget()
        party_widget.setLayout(party_layout)
        tabs.addTab(party_widget, "Parties")

        # Character Management Tab
        char_layout = QVBoxLayout()
        char_button_layout = QHBoxLayout()
        add_char_btn = QPushButton("+ Add Character")
        add_char_btn.clicked.connect(self._show_create_character_dialog)
        char_button_layout.addWidget(add_char_btn)
        char_button_layout.addStretch()
        char_layout.addLayout(char_button_layout)

        self.character_list = QListWidget()
        self.character_list.itemClicked.connect(self._on_character_selected)
        char_layout.addWidget(QLabel("Party Members:"))
        char_layout.addWidget(self.character_list)
        char_widget = QWidget()
        char_widget.setLayout(char_layout)
        tabs.addTab(char_widget, "Characters")

        # Party Details Tab
        details_layout = QVBoxLayout()
        self.party_details = QLabel("Select a party to view details")
        self.party_details.setWordWrap(True)
        self.party_details.setStyleSheet("background-color: #fffacd; padding: 10px; border-radius: 5px;")
        details_layout.addWidget(self.party_details)

        # Party details controls
        control_layout = QHBoxLayout()
        gold_label = QLabel("Adjust Gold:")
        self.gold_spin = QSpinBox()
        self.gold_spin.setRange(-10000, 100000)
        adjust_gold_btn = QPushButton("Update Gold")
        adjust_gold_btn.clicked.connect(self._adjust_party_gold)
        control_layout.addWidget(gold_label)
        control_layout.addWidget(self.gold_spin)
        control_layout.addWidget(adjust_gold_btn)
        control_layout.addStretch()
        details_layout.addLayout(control_layout)

        details_widget = QWidget()
        details_widget.setLayout(details_layout)
        tabs.addTab(details_widget, "Party Details")

        layout.addWidget(tabs)

    def _connect_signals(self):
        """Connect ViewModel signals."""
        self.viewmodel.party_created.connect(self._on_party_created)
        self.viewmodel.character_created.connect(self._on_character_created)
        self.viewmodel.party_members_loaded.connect(self._on_party_members_loaded)
        self.viewmodel.error_occurred.connect(self._on_error)

    def _show_create_party_dialog(self):
        """Show dialog to create a new party."""
        if not self.viewmodel.selected_campaign:
            QMessageBox.warning(self, "No Campaign", "Select a campaign first.")
            return

        dialog = CreatePartyDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.viewmodel.create_party(
                campaign_id=self.viewmodel.selected_campaign.id,
                name=data["name"],
                description=data["description"],
            )

    def _show_create_character_dialog(self):
        """Show dialog to create a new character."""
        if not self.current_party:
            QMessageBox.warning(self, "No Party", "Select a party first.")
            return

        dialog = CreateCharacterDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.viewmodel.create_character(
                party_id=self.current_party.id,
                name=data["name"],
                char_class=data["char_class"],
                level=data["level"],
                race=data["race"],
            )

    def _on_party_created(self, party):
        """Handle party created signal."""
        self.current_party = party
        self._load_parties()

    def _on_character_created(self, character):
        """Handle character created signal."""
        self._load_party_members()

    def _on_party_selected(self, item):
        """Handle party selection."""
        party_id = item.data(Qt.UserRole)
        party = self.viewmodel.get_party(party_id)
        if party:
            self.current_party = party
            details_text = f"<b>{party.name}</b><br>"
            details_text += f"Members: {len(party.character_ids)}<br>"
            details_text += f"Gold: {party.party_gold}<br>"
            if party.current_settlement_id:
                details_text += f"Location: {party.current_settlement_id}<br>"
            self.party_details.setText(details_text)
            self._load_party_members()

    def _on_party_members_loaded(self, characters):
        """Handle party members loaded signal."""
        self.characters = characters
        self.character_list.clear()
        for character in characters:
            item_text = f"{character.name} (Level {character.level} {character.character_class})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, character.id)
            self.character_list.addItem(item)

    def _on_character_selected(self, item):
        """Handle character selection."""
        character_id = item.data(Qt.UserRole)
        character = next((c for c in self.characters if c.id == character_id), None)
        if character:
            self.viewmodel.select_character(character_id)

    def _adjust_party_gold(self):
        """Adjust party gold."""
        if self.current_party:
            amount = self.gold_spin.value()
            self.viewmodel.update_party_gold(self.current_party.id, amount)

    def _load_parties(self):
        """Load parties from campaign."""
        if self.viewmodel.selected_campaign:
            # For now, just show the selected party
            if self.viewmodel.selected_party:
                self.party_list.clear()
                item_text = f"{self.viewmodel.selected_party.name}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, self.viewmodel.selected_party.id)
                self.party_list.addItem(item)

    def _load_party_members(self):
        """Load party members."""
        if self.current_party:
            self.viewmodel.load_party_members()

    def _on_error(self, error_msg):
        """Handle error signal."""
        QMessageBox.critical(self, "Error", error_msg)

    def showEvent(self, event):
        """Load data when page is shown."""
        super().showEvent(event)
        self._load_parties()

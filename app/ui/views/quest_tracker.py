"""Quest Tracker page for managing quests."""
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QFormLayout,
    QMessageBox,
    QTabWidget,
)
from PySide6.QtCore import Qt

from app.ui.viewmodels.campaign_viewmodel import CampaignViewModel


class CreateQuestDialog(QDialog):
    """Dialog for creating a new quest."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Quest")
        self.setMinimumWidth(450)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        self.title_input = QLineEdit()
        layout.addRow("Quest Title:", self.title_input)

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        layout.addRow("Description:", self.description_input)

        self.objectives_input = QTextEdit()
        self.objectives_input.setMaximumHeight(80)
        self.objectives_input.setPlaceholderText("One objective per line")
        layout.addRow("Objectives:", self.objectives_input)

        button_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        cancel_btn = QPushButton("Cancel")
        create_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def get_data(self):
        objectives = [
            line.strip() 
            for line in self.objectives_input.toPlainText().split('\n') 
            if line.strip()
        ]
        return {
            "title": self.title_input.text(),
            "description": self.description_input.toPlainText(),
            "objectives": objectives,
        }


class QuestTrackerPage(QWidget):
    """Quest Tracker for creating and managing quests."""

    def __init__(self, viewmodel: CampaignViewModel):
        super().__init__()
        self.viewmodel = viewmodel
        self.quests = []
        self.current_quest = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Quest Tracker")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #654321;")
        layout.addWidget(title)

        # Create quest button
        button_layout = QHBoxLayout()
        create_btn = QPushButton("+ Create New Quest")
        create_btn.clicked.connect(self._show_create_dialog)
        button_layout.addWidget(create_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Tab widget for quest views
        tabs = QTabWidget()

        # Active Quests Tab
        active_layout = QVBoxLayout()
        self.active_list = QListWidget()
        self.active_list.itemClicked.connect(self._on_quest_selected)
        active_layout.addWidget(QLabel("Active Quests:"))
        active_layout.addWidget(self.active_list)
        active_widget = QWidget()
        active_widget.setLayout(active_layout)
        tabs.addTab(active_widget, "Active")

        # Available Quests Tab
        available_layout = QVBoxLayout()
        self.available_list = QListWidget()
        self.available_list.itemClicked.connect(self._on_quest_selected)
        available_layout.addWidget(QLabel("Available Quests:"))
        available_layout.addWidget(self.available_list)
        available_widget = QWidget()
        available_widget.setLayout(available_layout)
        tabs.addTab(available_widget, "Available")

        # All Quests Tab
        all_layout = QVBoxLayout()
        self.all_list = QListWidget()
        self.all_list.itemClicked.connect(self._on_quest_selected)
        all_layout.addWidget(QLabel("All Quests:"))
        all_layout.addWidget(self.all_list)
        all_widget = QWidget()
        all_widget.setLayout(all_layout)
        tabs.addTab(all_widget, "All")

        layout.addWidget(tabs)

        # Quest details panel
        details_layout = QHBoxLayout()
        
        # Details
        self.details_label = QLabel("Select a quest to view details")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("background-color: #fffacd; padding: 10px; border-radius: 5px;")
        details_layout.addWidget(self.details_label, 1)
        
        # Action buttons
        button_layout = QVBoxLayout()
        self.accept_btn = QPushButton("Accept Quest")
        self.accept_btn.clicked.connect(self._accept_quest)
        self.accept_btn.setEnabled(False)
        button_layout.addWidget(self.accept_btn)
        
        self.complete_btn = QPushButton("Complete Quest")
        self.complete_btn.clicked.connect(self._complete_quest)
        self.complete_btn.setEnabled(False)
        button_layout.addWidget(self.complete_btn)
        
        self.abandon_btn = QPushButton("Abandon Quest")
        self.abandon_btn.clicked.connect(self._abandon_quest)
        self.abandon_btn.setEnabled(False)
        button_layout.addWidget(self.abandon_btn)
        
        button_layout.addStretch()
        details_layout.addLayout(button_layout)
        
        layout.addLayout(details_layout)

    def _connect_signals(self):
        """Connect ViewModel signals."""
        self.viewmodel.quests_loaded.connect(self._on_quests_loaded)
        self.viewmodel.quest_status_changed.connect(self._on_quest_status_changed)
        self.viewmodel.error_occurred.connect(self._on_error)

    def _show_create_dialog(self):
        """Show dialog to create a new quest."""
        if not self.viewmodel.selected_campaign:
            QMessageBox.warning(self, "No Campaign", "Select a campaign first.")
            return

        dialog = CreateQuestDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.viewmodel.create_quest(
                campaign_id=self.viewmodel.selected_campaign.id,
                title=data["title"],
                description=data["description"],
                objectives=data["objectives"],
                reward_experience=0,
                reward_gold=0,
            )

    def _on_quests_loaded(self, quests):
        """Handle quests loaded signal."""
        self.quests = quests
        self.active_list.clear()
        self.available_list.clear()
        self.all_list.clear()

        for quest in quests:
            item_text = f"{quest.title} ({quest.status})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, quest.id)

            if quest.status == "active":
                self.active_list.addItem(item)
            elif quest.status == "available":
                self.available_list.addItem(item)

            self.all_list.addItem(item)

    def _on_quest_selected(self, item):
        """Handle quest selection."""
        quest_id = item.data(Qt.UserRole)
        quest = next((q for q in self.quests if q.id == quest_id), None)

        if quest:
            self.current_quest = quest
            details_text = f"<b>{quest.title}</b><br>"
            details_text += f"Status: {quest.status}<br>"
            if quest.description:
                details_text += f"Description: {quest.description}<br>"
            if quest.objectives:
                details_text += f"Objectives:<ul>"
                for obj in quest.objectives:
                    details_text += f"<li>{obj}</li>"
                details_text += "</ul>"
            if quest.reward_xp:
                details_text += f"XP Reward: {quest.reward_xp}<br>"
            if quest.reward_gold:
                details_text += f"Gold Reward: {quest.reward_gold}<br>"
            self.details_label.setText(details_text)

            # Update button states based on quest status
            self.accept_btn.setEnabled(quest.status == "available")
            self.complete_btn.setEnabled(quest.status == "active")
            self.abandon_btn.setEnabled(quest.status == "active")

    def _accept_quest(self):
        """Accept the selected quest."""
        if self.current_quest:
            self.viewmodel.accept_quest(self.current_quest.id)

    def _complete_quest(self):
        """Complete the selected quest."""
        if self.current_quest:
            self.viewmodel.complete_quest(self.current_quest.id)

    def _abandon_quest(self):
        """Abandon the selected quest."""
        if self.current_quest:
            reply = QMessageBox.question(
                self, "Confirm Abandon",
                f"Are you sure you want to abandon '{self.current_quest.title}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.viewmodel.abandon_quest(self.current_quest.id)

    def _on_quest_status_changed(self, quest_id, new_status):
        """Handle quest status change."""
        self.viewmodel.load_campaign_quests()

    def _on_error(self, error_msg):
        """Handle error signal."""
        QMessageBox.critical(self, "Error", error_msg)

    def showEvent(self, event):
        """Load quests when page is shown."""
        super().showEvent(event)
        if self.viewmodel.selected_campaign:
            self.viewmodel.load_campaign_quests()

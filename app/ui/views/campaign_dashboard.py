"""Campaign Dashboard page for managing campaigns."""
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
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


class CreateCampaignDialog(QDialog):
    """Dialog for creating a new campaign."""

    def __init__(self, parent=None, worlds=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Campaign")
        self.setMinimumWidth(400)
        self.worlds = worlds or []
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        self.world_combo = QComboBox()
        if self.worlds:
            for world in self.worlds:
                self.world_combo.addItem(world.name, world.id)
        layout.addRow("World:", self.world_combo)

        self.name_input = QLineEdit()
        layout.addRow("Campaign Name:", self.name_input)

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        layout.addRow("Description:", self.description_input)

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard", "Deadly"])
        layout.addRow("Difficulty:", self.difficulty_combo)

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
            "world_id": self.world_combo.currentData(),
            "name": self.name_input.text(),
            "description": self.description_input.toPlainText(),
            "difficulty": self.difficulty_combo.currentText(),
        }


class CampaignDashboardPage(QWidget):
    """Campaign Dashboard for creating and managing campaigns."""

    def __init__(self, viewmodel: CampaignViewModel, persistence_service):
        super().__init__()
        self.viewmodel = viewmodel
        self.persistence_service = persistence_service
        self.campaigns = []
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Campaign Management Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #654321;")
        layout.addWidget(title)

        # Create campaign button
        button_layout = QHBoxLayout()
        create_btn = QPushButton("+ Create New Campaign")
        create_btn.clicked.connect(self._show_create_dialog)
        button_layout.addWidget(create_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Tab widget for different views
        tabs = QTabWidget()
        
        # Active Campaigns Tab
        active_layout = QVBoxLayout()
        self.active_list = QListWidget()
        self.active_list.itemClicked.connect(self._on_campaign_selected)
        active_layout.addWidget(QLabel("Active Campaigns:"))
        active_layout.addWidget(self.active_list)
        active_widget = QWidget()
        active_widget.setLayout(active_layout)
        tabs.addTab(active_widget, "Active Campaigns")
        
        # All Campaigns Tab
        all_layout = QVBoxLayout()
        self.all_list = QListWidget()
        self.all_list.itemClicked.connect(self._on_campaign_selected)
        all_layout.addWidget(QLabel("All Campaigns:"))
        all_layout.addWidget(self.all_list)
        all_widget = QWidget()
        all_widget.setLayout(all_layout)
        tabs.addTab(all_widget, "All Campaigns")
        
        layout.addWidget(tabs)

        # Campaign details panel
        details_layout = QHBoxLayout()
        
        # Details
        self.details_label = QLabel("Select a campaign to view details")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("background-color: #fffacd; padding: 10px; border-radius: 5px;")
        details_layout.addWidget(self.details_label)
        
        # Action buttons
        button_layout = QVBoxLayout()
        self.select_btn = QPushButton("Open Campaign")
        self.select_btn.clicked.connect(self._on_open_campaign)
        self.select_btn.setEnabled(False)
        button_layout.addWidget(self.select_btn)
        button_layout.addStretch()
        details_layout.addLayout(button_layout)
        
        layout.addLayout(details_layout)

    def _connect_signals(self):
        """Connect ViewModel signals."""
        self.viewmodel.campaigns_loaded.connect(self._on_campaigns_loaded)
        self.viewmodel.error_occurred.connect(self._on_error)

    def _show_create_dialog(self):
        """Show dialog to create a new campaign."""
        try:
            worlds = self.persistence_service.list_all_worlds()
            if not worlds:
                QMessageBox.warning(self, "No Worlds", "Create a world first before creating campaigns.")
                return
            
            dialog = CreateCampaignDialog(self, worlds)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_data()
                self.viewmodel.create_campaign(
                    world_id=data["world_id"],
                    name=data["name"],
                    description=data["description"],
                    difficulty=data["difficulty"],
                )
                self.viewmodel.load_all_campaigns()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create campaign: {str(e)}")

    def _on_campaigns_loaded(self, campaigns):
        """Handle campaigns loaded signal."""
        self.campaigns = campaigns
        self.active_list.clear()
        self.all_list.clear()
        
        for campaign in campaigns:
            item_text = f"{campaign.name} (World: {campaign.world_id})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, campaign.id)
            self.all_list.addItem(item)

    def _on_campaign_selected(self, item):
        """Handle campaign selection."""
        campaign_id = item.data(Qt.UserRole)
        campaign = next((c for c in self.campaigns if c.id == campaign_id), None)
        
        if campaign:
            details_text = f"<b>{campaign.name}</b><br>"
            details_text += f"World: {campaign.world_id}<br>"
            details_text += f"Description: {campaign.description}<br>"
            if campaign.party_id:
                details_text += f"Party ID: {campaign.party_id}<br>"
            self.details_label.setText(details_text)
            self.select_btn.setEnabled(True)
            self.current_campaign = campaign

    def _on_open_campaign(self):
        """Handle opening a campaign."""
        if hasattr(self, 'current_campaign'):
            self.viewmodel.select_campaign(self.current_campaign.id)
            QMessageBox.information(self, "Campaign Selected", 
                                   f"Campaign '{self.current_campaign.name}' selected. Use other campaign tabs to manage it.")

    def _on_error(self, error_msg):
        """Handle error signal."""
        QMessageBox.critical(self, "Error", error_msg)

    def showEvent(self, event):
        """Load campaigns when page is shown."""
        super().showEvent(event)
        self.viewmodel.load_all_campaigns()

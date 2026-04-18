"""World Overview page - Reimagined with modern card-based design."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFrame,
    QScrollArea,
    QGridLayout,
    QComboBox,
    QDialog,
    QFormLayout,
    QMessageBox,
    QTextEdit,
    QProgressBar,
    QGroupBox,
)

from app.ui.viewmodels.world_viewmodel import WorldOverviewViewModel
from app.domain.models.structure import World


class WorldCard(QFrame):
    """Modern card widget for displaying world information."""

    clicked = Signal(str)  # Emits world_id

    def __init__(self, world_data: Dict, parent=None):
        super().__init__(parent)
        self.world_data = world_data
        self.world = world_data["world"]
        self.setFixedSize(320, 280)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            WorldCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(244, 228, 188, 0.95),
                    stop:1 rgba(222, 184, 135, 0.9));
                border: 2px solid #daa520;
                border-radius: 15px;
                box-shadow: 0 4px 12px rgba(139, 69, 19, 0.3);
                margin: 8px;
            }
            WorldCard:hover {
                border-color: #cd853f;
                box-shadow: 0 6px 20px rgba(139, 69, 19, 0.4);
                transform: translateY(-2px);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Header with world name and icon
        header_layout = QHBoxLayout()
        icon_label = QLabel("🌍")
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)

        title_label = QLabel(self.world.name)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #654321;
                font-family: 'Times New Roman', serif;
            }
        """)
        header_layout.addWidget(title_label, 1)
        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(self.world.description or "A mysterious world awaits...")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #8b4513;
                font-size: 12px;
                font-family: 'Times New Roman', serif;
                margin-bottom: 8px;
            }
        """)
        desc_label.setMaximumHeight(40)
        layout.addWidget(desc_label)

        # Statistics grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(4)

        # Row 1
        continents_label = QLabel("🗺️ Continents:")
        continents_label.setStyleSheet("font-size: 11px; color: #654321; font-weight: bold;")
        stats_layout.addWidget(continents_label, 0, 0)

        continents_value = QLabel(str(self.world_data["continent_count"]))
        continents_value.setStyleSheet("font-size: 11px; color: #8b4513;")
        stats_layout.addWidget(continents_value, 0, 1)

        empires_label = QLabel("👑 Empires:")
        empires_label.setStyleSheet("font-size: 11px; color: #654321; font-weight: bold;")
        stats_layout.addWidget(empires_label, 0, 2)

        empires_value = QLabel(str(self.world_data["empire_count"]))
        empires_value.setStyleSheet("font-size: 11px; color: #8b4513;")
        stats_layout.addWidget(empires_value, 0, 3)

        # Row 2
        kingdoms_label = QLabel("🏰 Kingdoms:")
        kingdoms_label.setStyleSheet("font-size: 11px; color: #654321; font-weight: bold;")
        stats_layout.addWidget(kingdoms_label, 1, 0)

        kingdoms_value = QLabel(str(self.world_data["kingdom_count"]))
        kingdoms_value.setStyleSheet("font-size: 11px; color: #8b4513;")
        stats_layout.addWidget(kingdoms_value, 1, 1)

        regions_label = QLabel("🌄 Regions:")
        regions_label.setStyleSheet("font-size: 11px; color: #654321; font-weight: bold;")
        stats_layout.addWidget(regions_label, 1, 2)

        regions_value = QLabel(str(self.world_data["region_count"]))
        regions_value.setStyleSheet("font-size: 11px; color: #8b4513;")
        stats_layout.addWidget(regions_value, 1, 3)

        # Row 3
        settlements_label = QLabel("🏘️ Settlements:")
        settlements_label.setStyleSheet("font-size: 11px; color: #654321; font-weight: bold;")
        stats_layout.addWidget(settlements_label, 2, 0)

        settlements_value = QLabel(str(self.world_data["settlement_count"]))
        settlements_value.setStyleSheet("font-size: 11px; color: #8b4513;")
        stats_layout.addWidget(settlements_value, 2, 1)

        layout.addLayout(stats_layout)

        # Progress bar for world completeness
        completeness = self._calculate_completeness()
        progress_label = QLabel("World Completeness:")
        progress_label.setStyleSheet("font-size: 10px; color: #654321; font-weight: bold; margin-top: 8px;")
        layout.addWidget(progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(completeness)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #daa520;
                border-radius: 3px;
                text-align: center;
                background-color: rgba(222, 184, 135, 0.3);
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #32cd32,
                    stop:1 #228b22);
                border-radius: 2px;
            }
        """)
        self.progress_bar.setFixedHeight(12)
        layout.addWidget(self.progress_bar)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(4)

        self.view_btn = QPushButton("👁️ View")
        self.view_btn.setStyleSheet("""
            QPushButton {
                background-color: #daa520;
                color: #654321;
                border: 1px solid #cd853f;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cd853f;
            }
        """)
        self.view_btn.clicked.connect(lambda: self.clicked.emit(self.world.id))
        buttons_layout.addWidget(self.view_btn)

        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #87ceeb;
                color: #2e4a62;
                border: 1px solid #4682b4;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4682b4;
                color: white;
            }
        """)
        buttons_layout.addWidget(self.edit_btn)

        self.export_btn = QPushButton("📤 Export")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #98fb98;
                color: #2e8b57;
                border: 1px solid #32cd32;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #32cd32;
                color: white;
            }
        """)
        buttons_layout.addWidget(self.export_btn)

        layout.addLayout(buttons_layout)

        # Footer with creation date
        created_text = f"Created: {self.world.created_at.strftime('%Y-%m-%d') if hasattr(self.world, 'created_at') and self.world.created_at else 'Unknown'}"
        footer_label = QLabel(created_text)
        footer_label.setStyleSheet("""
            QLabel {
                font-size: 9px;
                color: #a0522d;
                font-style: italic;
                text-align: center;
            }
        """)
        layout.addWidget(footer_label)

    def _calculate_completeness(self) -> int:
        """Calculate world completeness percentage."""
        total_features = 5  # continents, empires, kingdoms, regions, settlements
        completed = 0

        if self.world_data["continent_count"] > 0:
            completed += 1
        if self.world_data["empire_count"] > 0:
            completed += 1
        if self.world_data["kingdom_count"] > 0:
            completed += 1
        if self.world_data["region_count"] > 0:
            completed += 1
        if self.world_data["settlement_count"] > 0:
            completed += 1

        return int((completed / total_features) * 100)

    def mousePressEvent(self, event):
        """Handle mouse click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.world.id)
        super().mousePressEvent(event)


class CreateWorldDialog(QDialog):
    """Modern dialog for creating new worlds."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New World")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f4e4bc,
                    stop:1 #daa520);
                border: 3px solid #cd853f;
                border-radius: 15px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header_label = QLabel("🌍 Create New World")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #654321;
                font-family: 'Times New Roman', serif;
                text-align: center;
            }
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)

        # Form
        form_group = QGroupBox("World Details")
        form_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #654321;
                font-family: 'Times New Roman', serif;
                border: 2px solid #daa520;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(15)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter world name...")
        self.name_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #daa520;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #cd853f;
                box-shadow: 0 0 5px rgba(205, 133, 63, 0.5);
            }
        """)
        form_layout.addRow("World Name:", self.name_input)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Describe your world...")
        self.desc_input.setMaximumHeight(80)
        self.desc_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #daa520;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #cd853f;
                box-shadow: 0 0 5px rgba(205, 133, 63, 0.5);
            }
        """)
        form_layout.addRow("Description:", self.desc_input)

        layout.addWidget(form_group)

        # Template selection
        template_group = QGroupBox("Starting Template")
        template_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #654321;
                font-family: 'Times New Roman', serif;
                border: 2px solid #daa520;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        template_layout = QVBoxLayout(template_group)

        self.template_combo = QComboBox()
        self.template_combo.addItem("🏰 Empty World - Start from scratch", "empty")
        self.template_combo.addItem("🌟 Sample World - Pre-populated with examples", "sample")
        self.template_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #daa520;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
        """)
        template_layout.addWidget(self.template_combo)

        layout.addWidget(template_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc143c;
                color: white;
                border: 2px solid #b22222;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
            }
            QPushButton:hover {
                background-color: #b22222;
                border-color: #8b0000;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        button_layout.addStretch()

        self.create_btn = QPushButton("✨ Create World")
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #32cd32;
                color: white;
                border: 2px solid #228b22;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
            }
            QPushButton:hover {
                background-color: #228b22;
                border-color: #006400;
            }
        """)
        self.create_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.create_btn)

        layout.addLayout(button_layout)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "description": self.desc_input.toPlainText().strip(),
            "template": self.template_combo.currentData(),
        }


class WorldOverviewPage(QWidget):
    """Reimagined World Overview with modern card-based design."""

    world_selected = Signal(str)  # Emits world_id

    def __init__(self, view_model: WorldOverviewViewModel):
        super().__init__()
        self.view_model = view_model
        self.world_cards = []
        self.selected_world_id = None
        self._setup_ui()
        self.refresh_worlds()

    def _setup_ui(self):
        """Setup the modern UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header section
        self._setup_header(main_layout)

        # Search and filter section
        self._setup_search_filter(main_layout)

        # Main content area with cards
        self._setup_content_area(main_layout)

        # Footer with stats
        self._setup_footer(main_layout)

    def _setup_header(self, parent_layout):
        """Setup the header section."""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(218, 165, 32, 0.9),
                    stop:1 rgba(139, 69, 19, 0.8));
                border: 3px solid #daa520;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 0 20px rgba(139, 69, 19, 0.4);
            }
        """)
        header_layout = QVBoxLayout(header_frame)

        title_layout = QHBoxLayout()
        title_icon = QLabel("🌍")
        title_icon.setStyleSheet("font-size: 36px;")
        title_layout.addWidget(title_icon)

        title_text = QLabel("World Library")
        title_text.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #f4e4bc;
                font-family: 'Times New Roman', serif;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            }
        """)
        title_layout.addWidget(title_text)
        title_layout.addStretch()

        self.create_world_btn = QPushButton("➕ Create World")
        self.create_world_btn.setStyleSheet("""
            QPushButton {
                background-color: #32cd32;
                color: white;
                border: 2px solid #228b22;
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                box-shadow: 0 0 10px rgba(50, 205, 50, 0.4);
            }
            QPushButton:hover {
                background-color: #228b22;
                box-shadow: 0 0 15px rgba(50, 205, 50, 0.6);
            }
        """)
        self.create_world_btn.clicked.connect(self._show_create_world_dialog)
        title_layout.addWidget(self.create_world_btn)

        header_layout.addLayout(title_layout)

        subtitle = QLabel("Discover, create, and manage your fantasy worlds")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(244, 228, 188, 0.9);
                font-size: 16px;
                font-family: 'Times New Roman', serif;
                font-style: italic;
                text-align: center;
            }
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)

        parent_layout.addWidget(header_frame)

    def _setup_search_filter(self, parent_layout):
        """Setup search and filter controls."""
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(244, 228, 188, 0.9);
                border: 2px solid #daa520;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setSpacing(15)

        # Search input
        search_label = QLabel("🔍 Search:")
        search_label.setStyleSheet("font-weight: bold; color: #654321;")
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search worlds by name or description...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #daa520;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
                min-width: 300px;
            }
            QLineEdit:focus {
                border-color: #cd853f;
                box-shadow: 0 0 5px rgba(205, 133, 63, 0.5);
            }
        """)
        self.search_input.textChanged.connect(self._filter_worlds)
        search_layout.addWidget(self.search_input)

        # Sort combo
        sort_label = QLabel("Sort by:")
        sort_label.setStyleSheet("font-weight: bold; color: #654321;")
        search_layout.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItem("📅 Recently Created", "created")
        self.sort_combo.addItem("📝 Name (A-Z)", "name")
        self.sort_combo.addItem("🏰 Most Populated", "population")
        self.sort_combo.addItem("⭐ Completeness", "completeness")
        self.sort_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #daa520;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                min-width: 150px;
            }
        """)
        self.sort_combo.currentIndexChanged.connect(self._sort_worlds)
        search_layout.addWidget(self.sort_combo)

        search_layout.addStretch()

        # Stats display
        self.stats_label = QLabel("No worlds yet")
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #654321;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 12px;
                background-color: rgba(222, 184, 135, 0.5);
                border-radius: 6px;
            }
        """)
        search_layout.addWidget(self.stats_label)

        parent_layout.addWidget(search_frame)

    def _setup_content_area(self, parent_layout):
        """Setup the main content area with scrollable card grid."""
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(244, 228, 188, 0.95);
                border: 2px solid #daa520;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        content_layout = QVBoxLayout(content_frame)

        # Scroll area for cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(222, 184, 135, 0.5);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #daa520;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #cd853f;
            }
        """)

        # Container for cards
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setContentsMargins(15, 15, 15, 15)

        # Empty state
        self.empty_state = QLabel("🌟 No worlds found. Click 'Create World' to get started!")
        self.empty_state.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #8b4513;
                font-family: 'Times New Roman', serif;
                text-align: center;
                padding: 40px;
            }
        """)
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cards_layout.addWidget(self.empty_state, 0, 0, 1, -1)

        self.scroll_area.setWidget(self.cards_container)
        content_layout.addWidget(self.scroll_area)

        parent_layout.addWidget(content_frame)

    def _setup_footer(self, parent_layout):
        """Setup footer with additional actions."""
        footer_frame = QFrame()
        footer_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(139, 69, 19, 0.1);
                border: 2px solid #daa520;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        footer_layout = QHBoxLayout(footer_frame)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #87ceeb;
                color: #2e4a62;
                border: 2px solid #4682b4;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4682b4;
                color: white;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_worlds)
        footer_layout.addWidget(self.refresh_btn)

        footer_layout.addStretch()

        self.import_btn = QPushButton("📥 Import World")
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #dda0dd;
                color: #4b0082;
                border: 2px solid #ba55d3;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ba55d3;
                color: white;
            }
        """)
        footer_layout.addWidget(self.import_btn)

        parent_layout.addWidget(footer_frame)

    def refresh_worlds(self):
        """Refresh the world cards display."""
        # Clear existing cards
        for card in self.world_cards:
            card.setParent(None)
            card.deleteLater()
        self.world_cards.clear()

        # Get world data
        worlds_data = self.view_model.list_worlds_with_counts()

        # Update stats
        total_worlds = len(worlds_data)
        total_settlements = sum(data["settlement_count"] for data in worlds_data)
        total_empires = sum(data["empire_count"] for data in worlds_data)

        if total_worlds == 0:
            self.stats_label.setText("No worlds yet")
            self.empty_state.show()
        else:
            self.stats_label.setText(f"{total_worlds} worlds • {total_settlements} settlements • {total_empires} empires")
            self.empty_state.hide()

            # Create cards
            row, col = 0, 0
            max_cols = 3

            for data in worlds_data:
                # Add region and continent counts to data
                data["region_count"] = len(self.view_model.persistence_service.list_regions(data["world"].id))
                data["continent_count"] = len(self.view_model.persistence_service.list_continents(data["world"].id))

                card = WorldCard(data)
                card.clicked.connect(self._on_world_card_clicked)
                card.edit_btn.clicked.connect(lambda checked, wid=data["world"].id: self._edit_world(wid))
                card.export_btn.clicked.connect(lambda checked, wid=data["world"].id: self._export_world(wid))

                self.world_cards.append(card)
                self.cards_layout.addWidget(card, row, col)

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

    def _filter_worlds(self, text):
        """Filter worlds based on search text."""
        text = text.lower()
        for card in self.world_cards:
            world_name = card.world.name.lower()
            world_desc = (card.world.description or "").lower()
            visible = text in world_name or text in world_desc
            card.setVisible(visible)

    def _sort_worlds(self, index):
        """Sort worlds based on selected criteria."""
        sort_key = self.sort_combo.currentData()

        def sort_func(card):
            if sort_key == "name":
                return card.world.name.lower()
            elif sort_key == "created":
                return card.world.created_at or ""
            elif sort_key == "population":
                return card.world_data["settlement_count"]
            elif sort_key == "completeness":
                return card._calculate_completeness()
            return card.world.name.lower()

        # Sort cards
        sorted_cards = sorted(self.world_cards, key=sort_func, reverse=(sort_key in ["created", "population", "completeness"]))

        # Re-layout cards
        for i, card in enumerate(sorted_cards):
            row = i // 3
            col = i % 3
            self.cards_layout.addWidget(card, row, col)

    def _on_world_card_clicked(self, world_id):
        """Handle world card click."""
        self.selected_world_id = world_id
        self.world_selected.emit(world_id)

    def _show_create_world_dialog(self):
        """Show the create world dialog."""
        dialog = CreateWorldDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "Invalid Input", "World name is required.")
                return

            try:
                if data["template"] == "sample":
                    world = self.view_model.create_sample_world(data["name"], data["description"])
                else:
                    world = self.view_model.create_world(data["name"], data["description"])

                QMessageBox.information(self, "Success", f"World '{world.name}' created successfully!")
                self.refresh_worlds()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create world: {str(e)}")

    def _edit_world(self, world_id):
        """Edit a world (placeholder for now)."""
        world = self.view_model.get_world_by_id(world_id)
        if world:
            QMessageBox.information(
                self,
                "Edit World",
                f"World editing for '{world.name}' will be implemented in the next update.\n\n"
                f"ID: {world.id}\n"
                f"Created: {world.created_at.strftime('%Y-%m-%d') if world.created_at else 'Unknown'}"
            )

    def _export_world(self, world_id):
        """Export a world."""
        world = self.view_model.get_world_by_id(world_id)
        if not world:
            return

        target = Path.cwd() / f"world_export_{world.name.replace(' ', '_')}_{world.id}.json"
        try:
            self.view_model.export_full_world(world, target)
            QMessageBox.information(
                self,
                "Export Successful",
                f"World '{world.name}' exported to:\n{target}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export world: {str(e)}")

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QFrame,
    QSpacerItem,
    QSizePolicy,
)

from app.ui.viewmodels.world_viewmodel import WorldOverviewViewModel


class WorldOverviewPage(QWidget):
    def __init__(self, view_model: WorldOverviewViewModel):
        super().__init__()
        self.view_model = view_model
        self._build_ui()
        self.refresh_world_list()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #daa520 0%, #cd853f 50%, #a0522d 100%);
                border: 3px solid #654321;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 
                    0 0 20px rgba(139, 69, 19, 0.6),
                    inset 0 0 15px rgba(0, 0, 0, 0.2);
            }
        """)
        header_layout = QVBoxLayout(header_frame)

        title = QLabel("🌍 World Overview")
        title.setStyleSheet("""
            QLabel {
                color: #f4e4bc;
                font-size: 32px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
                margin: 0;
            }
        """)
        header_layout.addWidget(title)

        subtitle = QLabel("Manage and explore your fantasy worlds")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(244, 228, 188, 0.9);
                font-size: 18px;
                font-family: 'Times New Roman', serif;
                font-style: italic;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
                margin: 0;
            }
        """)
        header_layout.addWidget(subtitle)

        layout.addWidget(header_frame)

        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(244, 228, 188, 0.95);
                background-image: 
                    radial-gradient(circle at 25% 25%, rgba(139, 69, 19, 0.08) 0%, transparent 50%),
                    radial-gradient(circle at 75% 75%, rgba(160, 82, 45, 0.06) 0%, transparent 50%);
                border: 2px solid #daa520;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 
                    0 0 15px rgba(139, 69, 19, 0.3),
                    inset 0 0 10px rgba(0, 0, 0, 0.1);
            }
        """)
        content_layout = QHBoxLayout(content_frame)
        content_layout.setSpacing(20)

        # Left panel: World list and info
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(244, 228, 188, 0.9);
                border: 2px solid #daa520;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)

        world_list_label = QLabel("🌍 Available Worlds")
        world_list_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #654321;
                font-family: 'Times New Roman', serif;
                margin-bottom: 5px;
            }
        """)
        left_layout.addWidget(world_list_label)

        self.world_list = QListWidget()
        self.world_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #daa520;
                border-radius: 8px;
                padding: 5px;
                background-color: rgba(244, 228, 188, 0.9);
                font-size: 14px;
                font-family: 'Times New Roman', serif;
                color: #654321;
                box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.1);
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(218, 165, 32, 0.3);
                background-color: rgba(222, 184, 135, 0.3);
                border-radius: 4px;
                margin: 1px;
                color: #654321;
            }
            QListWidget::item:selected {
                background-color: rgba(205, 133, 63, 0.8);
                color: #f4e4bc;
                border: 2px solid #daa520;
                box-shadow: 0 0 6px rgba(218, 165, 32, 0.6);
            }
            QListWidget::item:hover {
                background-color: rgba(222, 184, 135, 0.5);
            }
        """)
        left_layout.addWidget(self.world_list, 1)

        # World info panel
        self.world_info_frame = QFrame()
        self.world_info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(244, 228, 188, 0.95);
                border: 2px solid #cd853f;
                border-radius: 10px;
                padding: 12px;
                margin-top: 10px;
            }
        """)
        info_layout = QVBoxLayout(self.world_info_frame)
        info_layout.setSpacing(8)

        info_title = QLabel("📖 World Information")
        info_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #654321;
                font-family: 'Times New Roman', serif;
            }
        """)
        info_layout.addWidget(info_title)

        self.world_info_label = QLabel("Select a world to view details")
        self.world_info_label.setWordWrap(True)
        self.world_info_label.setStyleSheet("""
            QLabel {
                color: #654321;
                font-size: 12px;
                font-family: 'Times New Roman', serif;
                background-color: rgba(222, 184, 135, 0.5);
                padding: 8px;
                border-radius: 6px;
                min-height: 60px;
            }
        """)
        info_layout.addWidget(self.world_info_label)

        self.edit_world_button = QPushButton("✏️ Edit World Info")
        self.edit_world_button.setStyleSheet("""
            QPushButton {
                background-color: #daa520;
                background-image: linear-gradient(180deg, #daa520 0%, #cd853f 100%);
                color: #654321;
                border: 2px solid #a0522d;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                box-shadow: 0 0 6px rgba(139, 69, 19, 0.3);
            }
            QPushButton:hover {
                background-color: #cd853f;
                background-image: linear-gradient(180deg, #cd853f 0%, #a0522d 100%);
                border-color: #8b4513;
                box-shadow: 0 0 8px rgba(139, 69, 19, 0.5);
            }
            QPushButton:pressed {
                background-color: #a0522d;
                transform: translateY(1px);
            }
        """)
        self.edit_world_button.clicked.connect(self.edit_world_info)
        info_layout.addWidget(self.edit_world_button)

        left_layout.addWidget(self.world_info_frame)

        content_layout.addWidget(left_panel, 1)

        self.detail_panel = QFrame()
        self.detail_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(244, 228, 188, 0.95);
                background-image: 
                    radial-gradient(circle at 25% 25%, rgba(139, 69, 19, 0.08) 0%, transparent 50%),
                    radial-gradient(circle at 75% 75%, rgba(160, 82, 45, 0.06) 0%, transparent 50%);
                border: 2px solid #daa520;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 
                    0 0 15px rgba(139, 69, 19, 0.3),
                    inset 0 0 10px rgba(0, 0, 0, 0.1);
            }
        """)
        detail_layout = QVBoxLayout(self.detail_panel)
        detail_layout.setSpacing(12)

        self.detail_title = QLabel("World Hierarchy Details")
        self.detail_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #654321;
                font-family: 'Times New Roman', serif;
                margin-bottom: 10px;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
            }
        """)
        detail_layout.addWidget(self.detail_title)

        self.detail_summary = QLabel("Select a world to inspect its continents, empires, kingdoms, regions, and settlements.")
        self.detail_summary.setWordWrap(True)
        self.detail_summary.setStyleSheet("""
            QLabel {
                color: #654321;
                font-size: 16px;
                font-family: 'Times New Roman', serif;
                font-style: italic;
                background-color: rgba(244, 228, 188, 0.8);
                padding: 10px;
                border-radius: 8px;
                border: 1px solid rgba(218, 165, 32, 0.3);
            }
        """)
        detail_layout.addWidget(self.detail_summary)

        self.detail_counts = QLabel("")
        self.detail_counts.setWordWrap(True)
        self.detail_counts.setStyleSheet("""
            QLabel {
                color: #8b4513;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                background-color: rgba(244, 228, 188, 0.9);
                padding: 8px 12px;
                border-radius: 6px;
                border: 1px solid rgba(218, 165, 32, 0.4);
                margin-bottom: 10px;
            }
        """)
        detail_layout.addWidget(self.detail_counts)

        self.detail_entities = QLabel("")
        self.detail_entities.setWordWrap(True)
        self.detail_entities.setStyleSheet("""
            QLabel {
                color: #654321;
                font-size: 14px;
                font-family: 'Times New Roman', serif;
                background-color: rgba(244, 228, 188, 0.7);
                padding: 8px;
                border-radius: 6px;
                border: 1px solid rgba(218, 165, 32, 0.2);
            }
        """)
        detail_layout.addWidget(self.detail_entities)

        self.hierarchy_tree = QTreeWidget()
        self.hierarchy_tree.setHeaderLabels(["Type", "Name"])
        self.hierarchy_tree.setStyleSheet("""
            QTreeWidget {
                border: 3px solid #daa520;
                border-radius: 12px;
                background-color: rgba(244, 228, 188, 0.95);
                background-image: 
                    radial-gradient(circle at 10% 10%, rgba(139, 69, 19, 0.05) 0%, transparent 40%),
                    radial-gradient(circle at 90% 90%, rgba(160, 82, 45, 0.03) 0%, transparent 40%);
                font-size: 14px;
                font-family: 'Times New Roman', serif;
                color: #654321;
                alternate-background-color: rgba(222, 184, 135, 0.3);
                box-shadow: 
                    0 0 15px rgba(139, 69, 19, 0.3),
                    inset 0 0 10px rgba(0, 0, 0, 0.1);
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid rgba(218, 165, 32, 0.2);
            }
            QTreeWidget::item:selected {
                background-color: rgba(205, 133, 63, 0.8);
                color: #f4e4bc;
                border: 1px solid #daa520;
            }
            QTreeWidget::item:hover {
                background-color: rgba(222, 184, 135, 0.5);
            }
            QHeaderView::section {
                background-color: rgba(139, 69, 19, 0.8);
                color: #f4e4bc;
                padding: 8px;
                border: 1px solid #daa520;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
            }
        """)
        self.hierarchy_tree.setRootIsDecorated(True)
        self.hierarchy_tree.setIndentation(18)
        detail_layout.addWidget(self.hierarchy_tree, 1)

        detail_layout.addStretch()
        content_layout.addWidget(self.detail_panel, 2)

        layout.addWidget(content_frame)

        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(244, 228, 188, 0.9);
                background-image: 
                    radial-gradient(circle at 40% 60%, rgba(139, 69, 19, 0.08) 0%, transparent 50%);
                border: 2px solid #daa520;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 
                    0 0 12px rgba(139, 69, 19, 0.2),
                    inset 0 0 8px rgba(0, 0, 0, 0.05);
            }
        """)
        button_layout = QHBoxLayout(button_frame)

        self.new_world_button = QPushButton("✨ Create Sample World")
        self.new_world_button.setStyleSheet("""
            QPushButton {
                background-color: #228b22;
                background-image: linear-gradient(180deg, #32cd32 0%, #228b22 100%);
                color: #f4e4bc;
                border: 2px solid #006400;
                border-radius: 12px;
                padding: 14px 26px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                box-shadow: 0 0 10px rgba(34, 139, 34, 0.4);
            }
            QPushButton:hover {
                background-color: #32cd32;
                background-image: linear-gradient(180deg, #32cd32 0%, #006400 100%);
                border-color: #228b22;
                box-shadow: 0 0 15px rgba(34, 139, 34, 0.6);
            }
            QPushButton:pressed {
                background-color: #006400;
                transform: translateY(1px);
                box-shadow: 0 0 5px rgba(34, 139, 34, 0.8);
            }
        """)

        self.export_button = QPushButton("📤 Export Selected World")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #daa520;
                background-image: linear-gradient(180deg, #daa520 0%, #cd853f 100%);
                color: #654321;
                border: 2px solid #a0522d;
                border-radius: 12px;
                padding: 14px 26px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                box-shadow: 0 0 10px rgba(139, 69, 19, 0.4);
            }
            QPushButton:hover {
                background-color: #cd853f;
                background-image: linear-gradient(180deg, #cd853f 0%, #a0522d 100%);
                border-color: #8b4513;
                box-shadow: 0 0 15px rgba(139, 69, 19, 0.6);
            }
            QPushButton:pressed {
                background-color: #a0522d;
                transform: translateY(1px);
                box-shadow: 0 0 5px rgba(139, 69, 19, 0.8);
            }
        """)

        button_layout.addWidget(self.new_world_button)
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)

        layout.addWidget(button_frame)

        self.world_list.currentItemChanged.connect(self.on_world_selected)
        self.new_world_button.clicked.connect(self.create_sample_world)
        self.export_button.clicked.connect(self.export_selected_world)

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def refresh_world_list(self) -> None:
        self.world_list.clear()
        worlds_data = self.view_model.list_worlds_with_counts()
        if not worlds_data:
            self.world_list.addItem("No worlds created yet. Click 'Create Sample World' to get started! 🌟")
            self.render_world_details(None)
            self.update_world_info(None)
            return

        for data in worlds_data:
            world = data["world"]
            settlement_count = data["settlement_count"]
            kingdom_count = data["kingdom_count"]
            empire_count = data["empire_count"]
            display_text = f"🏰 {world.name}\n"
            display_text += f"   Settlements: {settlement_count} | Kingdoms: {kingdom_count} | Empires: {empire_count}\n"
            display_text += f"   ID: {world.id}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, world.id)
            self.world_list.addItem(item)

        self.world_list.setCurrentRow(0)

    def on_world_selected(self) -> None:
        current_item = self.world_list.currentItem()
        if not current_item:
            self.render_world_details(None)
            self.update_world_info(None)
            return

        world_id = current_item.data(Qt.UserRole)
        if not world_id:
            self.render_world_details(None)
            self.update_world_info(None)
            return

        details = self.view_model.load_world_details(world_id)
        self.render_world_details(details)
        self.update_world_info(details)

    def render_world_details(self, details: dict | None) -> None:
        if details is None or details.get("world") is None:
            self.detail_summary.setText("Select a world to inspect its continents, empires, kingdoms, regions, and settlements.")
            self.detail_counts.setText("")
            self.detail_entities.setText("")
            self.hierarchy_tree.clear()
            return

        world = details["world"]
        continents = details["continents"]
        empires = details["empires"]
        kingdoms = details["kingdoms"]
        regions = details["regions"]
        settlements = details["settlements"]

        self.detail_summary.setText(f"<b>{world.name}</b> — {world.description or 'A detailed campaign world.'}")
        self.detail_counts.setText(
            f"Continents: {len(continents)} | Empires: {len(empires)} | Kingdoms: {len(kingdoms)} | Regions: {len(regions)} | Settlements: {len(settlements)}"
        )

        entity_lines = []
        if continents:
            entity_lines.append("Continents: " + ", ".join(continent.name for continent in continents))
        if empires:
            entity_lines.append("Empires: " + ", ".join(empire.name for empire in empires))
        if kingdoms:
            entity_lines.append("Kingdoms: " + ", ".join(kingdom.name for kingdom in kingdoms))
        if regions:
            entity_lines.append("Regions: " + ", ".join(region.name for region in regions))
        if settlements:
            entity_lines.append("Settlements: " + ", ".join(settlement.name for settlement in settlements))

        self.detail_entities.setText("\n".join(entity_lines))
        self.render_hierarchy_tree(world.name, continents, empires, kingdoms, regions, settlements)

    def render_hierarchy_tree(
        self,
        world_name: str,
        continents: list,
        empires: list,
        kingdoms: list,
        regions: list,
        settlements: list,
    ) -> None:
        self.hierarchy_tree.clear()

        world_item = QTreeWidgetItem(["World", world_name])
        self.hierarchy_tree.addTopLevelItem(world_item)

        continent_items = {}
        for continent in continents:
            continent_item = QTreeWidgetItem(["Continent", continent.name])
            world_item.addChild(continent_item)
            continent_items[continent.id] = continent_item

        empire_items = {}
        for empire in empires:
            parent = continent_items.get(empire.continent_id, world_item)
            empire_item = QTreeWidgetItem(["Empire", empire.name])
            parent.addChild(empire_item)
            empire_items[empire.id] = empire_item

        kingdom_items = {}
        for kingdom in kingdoms:
            parent = empire_items.get(kingdom.empire_id) or continent_items.get(kingdom.continent_id, world_item)
            kingdom_item = QTreeWidgetItem(["Kingdom", kingdom.name])
            parent.addChild(kingdom_item)
            kingdom_items[kingdom.id] = kingdom_item

        region_items = {}
        for region in regions:
            parent = kingdom_items.get(region.kingdom_id) or empire_items.get(region.empire_id) or continent_items.get(region.continent_id, world_item)
            region_item = QTreeWidgetItem(["Region", region.name])
            parent.addChild(region_item)
            region_items[region.id] = region_item

        for settlement in settlements:
            parent = (
                region_items.get(settlement.region_id)
                or kingdom_items.get(settlement.kingdom_id)
                or empire_items.get(settlement.empire_id)
                or continent_items.get(settlement.continent_id)
                or world_item
            )
            settlement_item = QTreeWidgetItem(["Settlement", settlement.name])
            parent.addChild(settlement_item)

        self.hierarchy_tree.expandAll()

    def create_sample_world(self) -> None:
        self.view_model.create_sample_world(
            name="New Campaign World",
            description="A fresh world generated for campaign building.",
        )
        self.refresh_world_list()

    def export_selected_world(self) -> None:
        current_item = self.world_list.currentItem()
        if not current_item:
            return

        world_id = current_item.data(Qt.UserRole)
        if not world_id:
            return

        world = self.view_model.get_world_by_id(world_id)
        if not world:
            return

        target = Path.cwd() / f"world_export_{world.name.replace(' ', '_')}_{world.id}.json"
        self.view_model.export_full_world(world, target)

    def update_world_info(self, details: dict | None) -> None:
        if details is None or details.get("world") is None:
            self.world_info_label.setText("Select a world to view details")
            self.edit_world_button.setEnabled(False)
            return

        world = details["world"]
        continents = details["continents"]
        empires = details["empires"]
        kingdoms = details["kingdoms"]
        regions = details["regions"]
        settlements = details["settlements"]

        info_text = f"<b>{world.name}</b><br>"
        info_text += f"ID: {world.id}<br>"
        info_text += f"Created: {world.created_at.strftime('%Y-%m-%d') if hasattr(world, 'created_at') else 'Unknown'}<br><br>"
        info_text += f"Continents: {len(continents)}<br>"
        info_text += f"Empires: {len(empires)}<br>"
        info_text += f"Kingdoms: {len(kingdoms)}<br>"
        info_text += f"Regions: {len(regions)}<br>"
        info_text += f"Settlements: {len(settlements)}"

        self.world_info_label.setText(info_text)
        self.edit_world_button.setEnabled(True)

    def edit_world_info(self) -> None:
        current_item = self.world_list.currentItem()
        if not current_item:
            return

        world_id = current_item.data(Qt.UserRole)
        if not world_id:
            return

        world = self.view_model.get_world_by_id(world_id)
        if not world:
            return

        # TODO: Implement world editing dialog
        # For now, just show a message
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Edit World",
            f"World editing dialog for '{world.name}' would open here.\n\nThis feature will be implemented next."
        )

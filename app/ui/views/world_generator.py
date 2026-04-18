from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.ui.viewmodels.world_viewmodel import WorldOverviewViewModel


class WorldGeneratorPage(QWidget):
    def __init__(self, view_model: WorldOverviewViewModel):
        super().__init__()
        self.view_model = view_model
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
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

        title = QLabel("🧙‍♂️ World Generator")
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

        subtitle = QLabel("Answer the questions below to generate a custom world")
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

        # Scrollable form area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #daa520;
                border-radius: 15px;
                background-color: rgba(244, 228, 188, 0.95);
                box-shadow: 
                    0 0 15px rgba(139, 69, 19, 0.3),
                    inset 0 0 10px rgba(0, 0, 0, 0.1);
            }
            QScrollBar:vertical {
                background-color: rgba(139, 69, 19, 0.2);
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

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)

        # Basic Information Section
        basic_section = self._create_section("📝 Basic Information")
        basic_form = QFormLayout()
        basic_form.setSpacing(10)

        self.world_name_input = QLineEdit()
        self.world_name_input.setPlaceholderText("Enter world name...")
        self.world_name_input.setStyleSheet(self._input_style())
        basic_form.addRow("World Name:", self.world_name_input)

        self.world_description_input = QTextEdit()
        self.world_description_input.setPlaceholderText("Describe your world...")
        self.world_description_input.setMaximumHeight(80)
        self.world_description_input.setStyleSheet(self._textedit_style())
        basic_form.addRow("Description:", self.world_description_input)

        basic_section.layout().addLayout(basic_form)
        form_layout.addWidget(basic_section)

        # Geography Section
        geo_section = self._create_section("🌍 Geography")
        geo_form = QFormLayout()
        geo_form.setSpacing(10)

        self.continent_count = QSpinBox()
        self.continent_count.setRange(1, 10)
        self.continent_count.setValue(3)
        self.continent_count.setStyleSheet(self._spinbox_style())
        geo_form.addRow("Number of Continents:", self.continent_count)

        self.climate_combo = QComboBox()
        self.climate_combo.addItems(["Temperate", "Tropical", "Arid", "Polar", "Mixed"])
        self.climate_combo.setStyleSheet(self._combobox_style())
        geo_form.addRow("Primary Climate:", self.climate_combo)

        geo_section.layout().addLayout(geo_form)
        form_layout.addWidget(geo_section)

        # Political Section
        political_section = self._create_section("👑 Political Structure")
        political_form = QFormLayout()
        political_form.setSpacing(10)

        self.government_type_combo = QComboBox()
        self.government_type_combo.addItems([
            "Feudal Kingdoms", "Tribal Clans", "Magocratic Councils",
            "Merchant Republics", "Theocratic States", "Warlord Territories"
        ])
        self.government_type_combo.setStyleSheet(self._combobox_style())
        political_form.addRow("Government Type:", self.government_type_combo)

        self.tech_level_combo = QComboBox()
        self.tech_level_combo.addItems([
            "Medieval", "Renaissance", "Bronze Age", "Iron Age", "Stone Age"
        ])
        self.tech_level_combo.setStyleSheet(self._combobox_style())
        political_form.addRow("Technology Level:", self.tech_level_combo)

        political_section.layout().addLayout(political_form)
        form_layout.addWidget(political_section)

        # Magic Section
        magic_section = self._create_section("🔮 Magic & Supernatural")
        magic_form = QFormLayout()
        magic_form.setSpacing(10)

        self.magic_level_combo = QComboBox()
        self.magic_level_combo.addItems([
            "None", "Low", "Moderate", "High", "Wild Magic"
        ])
        self.magic_level_combo.setStyleSheet(self._combobox_style())
        magic_form.addRow("Magic Prevalence:", self.magic_level_combo)

        self.races_combo = QComboBox()
        self.races_combo.addItems([
            "Human Dominant", "Elven Kingdoms", "Dwarven Clans",
            "Mixed Fantasy", "Custom Mix"
        ])
        self.races_combo.setStyleSheet(self._combobox_style())
        magic_form.addRow("Racial Composition:", self.races_combo)

        magic_section.layout().addLayout(magic_form)
        form_layout.addWidget(magic_section)

        # Generate button
        generate_button = QPushButton("🎲 Generate World")
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #228b22;
                background-image: linear-gradient(180deg, #32cd32 0%, #228b22 100%);
                color: #f4e4bc;
                border: 2px solid #006400;
                border-radius: 12px;
                padding: 16px 32px;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Times New Roman', serif;
                box-shadow: 0 0 12px rgba(34, 139, 34, 0.4);
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #32cd32;
                background-image: linear-gradient(180deg, #32cd32 0%, #006400 100%);
                border-color: #228b22;
                box-shadow: 0 0 18px rgba(34, 139, 34, 0.6);
            }
            QPushButton:pressed {
                background-color: #006400;
                transform: translateY(1px);
                box-shadow: 0 0 8px rgba(34, 139, 34, 0.8);
            }
        """)
        generate_button.clicked.connect(self.generate_world)
        form_layout.addWidget(generate_button, alignment=Qt.AlignCenter)

        scroll_area.setWidget(form_widget)
        layout.addWidget(scroll_area, 1)

    def _create_section(self, title: str) -> QFrame:
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: rgba(222, 184, 135, 0.8);
                border: 2px solid #cd853f;
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
            }
        """)
        layout = QVBoxLayout(section)

        section_title = QLabel(title)
        section_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #654321;
                font-family: 'Times New Roman', serif;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(section_title)

        return section

    def _input_style(self) -> str:
        return """
            QLineEdit {
                border: 2px solid #daa520;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: rgba(244, 228, 188, 0.9);
                font-size: 14px;
                font-family: 'Times New Roman', serif;
                color: #654321;
            }
            QLineEdit:focus {
                border-color: #cd853f;
                background-color: rgba(222, 184, 135, 0.9);
                box-shadow: 0 0 6px rgba(218, 165, 32, 0.4);
            }
        """

    def _textedit_style(self) -> str:
        return """
            QTextEdit {
                border: 2px solid #daa520;
                border-radius: 6px;
                padding: 8px;
                background-color: rgba(244, 228, 188, 0.9);
                font-size: 14px;
                font-family: 'Times New Roman', serif;
                color: #654321;
            }
            QTextEdit:focus {
                border-color: #cd853f;
                box-shadow: 0 0 6px rgba(218, 165, 32, 0.4);
            }
        """

    def _combobox_style(self) -> str:
        return """
            QComboBox {
                border: 2px solid #daa520;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: rgba(244, 228, 188, 0.9);
                font-size: 14px;
                font-family: 'Times New Roman', serif;
                color: #654321;
            }
            QComboBox:hover {
                border-color: #cd853f;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(244, 228, 188, 0.95);
                border: 1px solid #daa520;
                selection-background-color: rgba(205, 133, 63, 0.8);
                color: #654321;
            }
        """

    def _spinbox_style(self) -> str:
        return """
            QSpinBox {
                border: 2px solid #daa520;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: rgba(244, 228, 188, 0.9);
                font-size: 14px;
                font-family: 'Times New Roman', serif;
                color: #654321;
            }
            QSpinBox:focus {
                border-color: #cd853f;
                box-shadow: 0 0 6px rgba(218, 165, 32, 0.4);
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #daa520;
                border: 1px solid #cd853f;
                width: 16px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #cd853f;
            }
        """

    def generate_world(self) -> None:
        # TODO: Implement world generation based on form inputs
        from PySide6.QtWidgets import QMessageBox

        name = self.world_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Information", "Please enter a world name.")
            return

        description = self.world_description_input.toPlainText().strip()

        # For now, create a basic world
        try:
            world = self.view_model.create_world(name, description)
            QMessageBox.information(
                self,
                "World Generated",
                f"Successfully created world '{world.name}'!\n\n"
                f"ID: {world.id}\n\n"
                f"Advanced world generation with custom parameters will be implemented next."
            )

            # Clear form
            self.world_name_input.clear()
            self.world_description_input.clear()

        except Exception as e:
            QMessageBox.critical(self, "Generation Failed", f"Failed to generate world: {e}")
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
    QFrame,
    QComboBox,
    QSpinBox,
    QPushButton,
    QProgressBar,
    QTextEdit,
    QTabWidget,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QFormLayout,
    QSplitter,
)
from PySide6.QtGui import QFont

from app.ui.viewmodels.simulation_viewmodel import SimulationViewModel
from app.domain.models.structure import World
from app.domain.simulation.runner import SimulationRun


class SimulationPage(QWidget):
    def __init__(self, view_model: SimulationViewModel):
        super().__init__()
        self.view_model = view_model
        self._setup_connections()
        self._build_ui()

    def _setup_connections(self) -> None:
        """Connect view model signals to UI updates."""
        self.view_model.worlds_loaded.connect(self._on_worlds_loaded)
        self.view_model.simulation_started.connect(self._on_simulation_started)
        self.view_model.simulation_progress.connect(self._on_simulation_progress)
        self.view_model.simulation_completed.connect(self._on_simulation_completed)
        self.view_model.simulation_error.connect(self._on_simulation_error)

    def _build_ui(self) -> None:
        """Build the simulation UI layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel: Controls
        controls_widget = self._build_controls_panel()
        splitter.addWidget(controls_widget)

        # Right panel: Results
        results_widget = self._build_results_panel()
        splitter.addWidget(results_widget)

        # Set splitter proportions
        splitter.setSizes([400, 800])

    def _build_controls_panel(self) -> QWidget:
        """Build the controls panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header
        header = QLabel("🎲 World Simulation")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(header)

        # World selection
        world_group = QGroupBox("World Selection")
        world_layout = QVBoxLayout(world_group)

        self.world_combo = QComboBox()
        self.world_combo.setPlaceholderText("Select a world...")
        self.world_combo.currentTextChanged.connect(self._on_world_selected)
        world_layout.addWidget(QLabel("World:"))
        world_layout.addWidget(self.world_combo)

        layout.addWidget(world_group)

        # Simulation controls
        sim_group = QGroupBox("Simulation Controls")
        sim_layout = QFormLayout(sim_group)

        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 3650)  # 1 day to 10 years
        self.days_spin.setValue(365)  # Default 1 year
        sim_layout.addRow("Days:", self.days_spin)

        self.run_button = QPushButton("▶️ Run Simulation")
        self.run_button.clicked.connect(self._on_run_simulation)
        sim_layout.addRow(self.run_button)

        layout.addWidget(sim_group)

        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)

        layout.addWidget(progress_group)

        # Load worlds button
        load_button = QPushButton("🔄 Load Worlds")
        load_button.clicked.connect(self._on_load_worlds)
        layout.addWidget(load_button)

        layout.addStretch()
        return panel

    def _build_results_panel(self) -> QWidget:
        """Build the results panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Results header
        results_header = QLabel("📊 Simulation Results")
        results_header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(results_header)

        # Results tabs
        self.results_tabs = QTabWidget()

        # Summary tab
        summary_tab = self._build_summary_tab()
        self.results_tabs.addTab(summary_tab, "Summary")

        # Events tab
        events_tab = self._build_events_tab()
        self.results_tabs.addTab(events_tab, "Events")

        # History tab
        history_tab = self._build_history_tab()
        self.results_tabs.addTab(history_tab, "History")

        layout.addWidget(self.results_tabs)

        return panel

    def _build_summary_tab(self) -> QWidget:
        """Build the summary results tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setPlainText("No simulation results yet.\n\nRun a simulation to see changes in population, NPCs, and world state.")
        layout.addWidget(self.summary_text)

        return tab

    def _build_events_tab(self) -> QWidget:
        """Build the events results tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.events_list = QListWidget()
        self.events_list.addItem("No events recorded yet.")
        layout.addWidget(self.events_list)

        return tab

    def _build_history_tab(self) -> QWidget:
        """Build the simulation history tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.history_list = QListWidget()
        self.history_list.addItem("No simulation history yet.")
        layout.addWidget(self.history_list)

        clear_button = QPushButton("🗑️ Clear History")
        clear_button.clicked.connect(self._on_clear_history)
        layout.addWidget(clear_button)

        return tab

    def _on_load_worlds(self) -> None:
        """Handle load worlds button click."""
        self.view_model.load_worlds()

    def _on_world_selected(self, world_name: str) -> None:
        """Handle world selection change."""
        if world_name and self.world_combo.currentData():
            world_id = self.world_combo.currentData()
            self.view_model.select_world(world_id)

    def _on_run_simulation(self) -> None:
        """Handle run simulation button click."""
        days = self.days_spin.value()
        self.view_model.run_simulation(days)

    def _on_clear_history(self) -> None:
        """Handle clear history button click."""
        self.view_model.clear_history()
        self.history_list.clear()
        self.history_list.addItem("History cleared.")

    def _on_worlds_loaded(self, worlds: List[World]) -> None:
        """Handle worlds loaded signal."""
        self.world_combo.clear()
        for world in worlds:
            self.world_combo.addItem(f"{world.name} ({world.id[:8]}...)", world.id)

        self.status_label.setText(f"Loaded {len(worlds)} worlds")

    def _on_simulation_started(self) -> None:
        """Handle simulation started signal."""
        self.progress_bar.setVisible(True)
        self.run_button.setEnabled(False)
        self.status_label.setText("Running simulation...")

    def _on_simulation_progress(self, message: str) -> None:
        """Handle simulation progress signal."""
        self.status_label.setText(message)

    def _on_simulation_completed(self, run: SimulationRun) -> None:
        """Handle simulation completed signal."""
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.status_label.setText("Simulation completed")

        # Update results
        self._update_results(run)

    def _on_simulation_error(self, error: str) -> None:
        """Handle simulation error signal."""
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.status_label.setText(f"Error: {error}")

    def _update_results(self, run: SimulationRun) -> None:
        """Update the UI with simulation results."""
        # Update summary
        summary = f"""Simulation Results
Duration: {run.duration.days} days

World Changes:
- Population changes: {len(run.changes.settlement_changes) if run.changes.settlement_changes else 0} settlements affected
- NPC changes: {len(run.changes.npc_changes) if run.changes.npc_changes else 0} NPCs affected
- Relationship changes: {len(run.changes.relationship_changes) if run.changes.relationship_changes else 0} relationships affected

Events: {len(run.events)} events occurred
"""

        self.summary_text.setPlainText(summary)

        # Update events
        self.events_list.clear()
        if run.events:
            for event in run.events:
                item = QListWidgetItem(f"{event.occurred_at}: {event.effect_summary}")
                self.events_list.addItem(item)
        else:
            self.events_list.addItem("No events occurred during this simulation.")

        # Update history
        history_item = QListWidgetItem(
            f"{run.created_at.strftime('%Y-%m-%d %H:%M')}: {run.duration.days} days, "
            f"{len(run.events)} events, {len(run.changes.npc_changes or [])} NPC changes"
        )
        self.history_list.addItem(history_item)
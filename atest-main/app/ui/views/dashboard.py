from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QWidget,
    QPushButton,
    QTextEdit,
)

from app.ui.viewmodels.dashboard_viewmodel import DashboardViewModel


class DashboardPage(QWidget):
    def __init__(self, view_model: DashboardViewModel, simulation_service):
        super().__init__()
        self.view_model = view_model
        self.sim = simulation_service

        self._build_ui()
        self._start_tick_timer()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Dashboard")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # Summary
        summary = QLabel(self.view_model.get_summary())
        summary.setAlignment(Qt.AlignTop)
        summary.setWordWrap(True)
        layout.addWidget(summary)

        # Tick counter
        self.tick_label = QLabel("Tick: 0")
        self.tick_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.tick_label)

        # Buttons
        self.start_btn = QPushButton("Start Simulation")
        self.stop_btn = QPushButton("Stop Simulation")
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        # Event log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        # Connect signals
        self.start_btn.clicked.connect(self._on_start)
        self.stop_btn.clicked.connect(self._on_stop)

    def _on_start(self):
        self.sim.start()
        self.log.append("Simulation started.")

    def _on_stop(self):
        self.sim.stop()
        self.log.append("Simulation stopped.")

    def _start_tick_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_tick)
        self.timer.start(200)  # update 5 times per second

    def _update_tick(self):
        tick = self.sim.engine.current_tick
        self.tick_label.setText(f"Tick: {tick}")

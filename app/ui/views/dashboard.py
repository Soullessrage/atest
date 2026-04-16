from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget

from app.ui.viewmodels.dashboard_viewmodel import DashboardViewModel


class DashboardPage(QWidget):
    def __init__(self, view_model: DashboardViewModel):
        super().__init__()
        self.view_model = view_model
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        header = QLabel("Dashboard")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        summary = QLabel(self.view_model.get_summary())
        summary.setAlignment(Qt.AlignTop)
        summary.setWordWrap(True)
        layout.addWidget(summary)

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy

from app.ui.viewmodels.dashboard_viewmodel import DashboardViewModel


class DashboardPage(QWidget):
    def __init__(self, view_model: DashboardViewModel):
        super().__init__()
        self.view_model = view_model
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header section
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("🏠 Dashboard")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                margin: 0;
            }
        """)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Welcome to your D&D World Simulator")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 16px;
                margin: 0;
            }
        """)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_frame)

        # Summary section
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e1e5e9;
                padding: 20px;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        
        summary_title = QLabel("📊 World Summary")
        summary_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        summary_layout.addWidget(summary_title)

        summary = QLabel(self.view_model.get_summary())
        summary.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        summary.setWordWrap(True)
        summary_layout.addWidget(summary)
        
        layout.addWidget(summary_frame)
        
        # Add spacer to push content to top
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

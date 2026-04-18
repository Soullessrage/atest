"""Session Journal page for recording and viewing campaign sessions."""
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QFormLayout,
    QMessageBox,
)
from PySide6.QtCore import Qt

from app.ui.viewmodels.campaign_viewmodel import CampaignViewModel


class RecordSessionDialog(QDialog):
    """Dialog for recording a new session."""

    def __init__(self, parent=None, next_session=1):
        super().__init__(parent)
        self.setWindowTitle("Record Session")
        self.setMinimumWidth(500)
        self.next_session = next_session
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        self.session_spin = QSpinBox()
        self.session_spin.setValue(self.next_session)
        self.session_spin.setMinimum(1)
        layout.addRow("Session Number:", self.session_spin)

        self.summary_input = QTextEdit()
        self.summary_input.setMinimumHeight(120)
        layout.addRow("Summary:", self.summary_input)

        self.notes_input = QTextEdit()
        self.notes_input.setMinimumHeight(80)
        self.notes_input.setPlaceholderText("Additional notes (optional)")
        layout.addRow("Notes:", self.notes_input)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Session")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def get_data(self):
        return {
            "session_number": self.session_spin.value(),
            "summary": self.summary_input.toPlainText(),
            "notes": self.notes_input.toPlainText(),
        }


class SessionJournalPage(QWidget):
    """Session Journal for recording and viewing campaign sessions."""

    def __init__(self, viewmodel: CampaignViewModel):
        super().__init__()
        self.viewmodel = viewmodel
        self.journal_entries = []
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Campaign Journal")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #654321;")
        layout.addWidget(title)

        # Record session button
        button_layout = QHBoxLayout()
        record_btn = QPushButton("+ Record New Session")
        record_btn.clicked.connect(self._show_record_dialog)
        button_layout.addWidget(record_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Sessions list
        self.sessions_list = QListWidget()
        self.sessions_list.itemClicked.connect(self._on_session_selected)
        layout.addWidget(QLabel("Sessions:"))
        layout.addWidget(self.sessions_list, 1)

        # Session details panel
        details_layout = QVBoxLayout()
        self.details_label = QLabel("Select a session to view details")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("background-color: #fffacd; padding: 10px; border-radius: 5px;")
        details_layout.addWidget(self.details_label)

        layout.addLayout(details_layout, 1)

    def _connect_signals(self):
        """Connect ViewModel signals."""
        self.viewmodel.journal_loaded.connect(self._on_journal_loaded)
        self.viewmodel.session_recorded.connect(self._on_session_recorded)
        self.viewmodel.error_occurred.connect(self._on_error)

    def _show_record_dialog(self):
        """Show dialog to record a new session."""
        if not self.viewmodel.selected_campaign:
            QMessageBox.warning(self, "No Campaign", "Select a campaign first.")
            return

        next_session = len(self.journal_entries) + 1
        dialog = RecordSessionDialog(self, next_session)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.viewmodel.record_session(
                session_number=data["session_number"],
                summary=data["summary"],
                highlights=[data["notes"]] if data["notes"] else [],
            )

    def _on_journal_loaded(self, entries):
        """Handle journal loaded signal."""
        self.journal_entries = entries
        self.sessions_list.clear()

        for entry in entries:
            item_text = f"Session {entry.session_number}: {entry.content[:40]}..."
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, entry.id)
            self.sessions_list.addItem(item)

    def _on_session_selected(self, item):
        """Handle session selection."""
        entry_id = item.data(Qt.UserRole)
        entry = next((e for e in self.journal_entries if e.id == entry_id), None)

        if entry:
            details_text = f"<b>Session {entry.session_number}</b><br>"
            details_text += f"Date: {entry.session_date}<br><br>"
            details_text += f"<b>Summary:</b><br>{entry.content}<br><br>"
            if entry.notes:
                details_text += f"<b>Notes:</b><br>{entry.notes}<br><br>"
            if entry.events:
                details_text += f"<b>Events:</b><ul>"
                for event in entry.events:
                    details_text += f"<li>{event}</li>"
                details_text += "</ul>"
            self.details_label.setText(details_text)

    def _on_session_recorded(self, entry):
        """Handle session recorded signal."""
        self.viewmodel.load_campaign_journal()
        QMessageBox.information(
            self,
            "Session Recorded",
            f"Session {entry.session_number} has been recorded successfully!"
        )

    def _on_error(self, error_msg):
        """Handle error signal."""
        QMessageBox.critical(self, "Error", error_msg)

    def showEvent(self, event):
        """Load journal when page is shown."""
        super().showEvent(event)
        if self.viewmodel.selected_campaign:
            self.viewmodel.load_campaign_journal()

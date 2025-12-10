"""Competitor dashboard for CyberPatriot Runbook."""

from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Signal

class CompetitorDashboard(QMainWindow):
    """Dashboard for competitors."""
    user_logged_out = Signal()

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"CyberPatriot Runbook - Competitor Dashboard ({user['name']})")
        self.setGeometry(100, 100, 1200, 700)
        layout = QVBoxLayout()
        label = QLabel(f"Welcome, {user['name']}! This is your competitor dashboard.")
        layout.addWidget(label)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

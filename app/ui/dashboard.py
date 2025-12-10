"""
Dashboard skeleton with professional styling and role-based sections.
- Header with user welcome
- Navigation tabs for Checklists, Readmes, Forensic Qs, Notes, Settings
- Placeholder content for each section
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QFrame, QPushButton
)
from PySide6.QtGui import QFont
from ..styles import STYLESHEET


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(STYLESHEET)
        self.init_ui()

    def init_ui(self):
        """Initialize dashboard with professional layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header bar
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1e40af;
                border: none;
                padding: 20px;
                border-radius: 0;
            }
        """)
        header.setMinimumHeight(80)

        header_layout = QHBoxLayout(header)

        # Welcome message
        welcome = QLabel("Welcome to CyberPatriot Runbook")
        welcome.setFont(QFont("Segoe UI", 18, QFont.Bold))
        welcome.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(welcome)

        # Logout button (placeholder)
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        logout_btn.setMaximumWidth(120)
        header_layout.addStretch()
        header_layout.addWidget(logout_btn)

        main_layout.addWidget(header)

        # Tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet(STYLESHEET)

        # Checklists tab
        checklists_widget = QWidget()
        checklists_layout = QVBoxLayout(checklists_widget)
        checklists_layout.addWidget(QLabel("Checklists"))
        checklists_layout.addWidget(QLabel("Click items to expand. Mark status as Completed, Not Completed, or Skipped."))
        checklists_layout.addStretch()
        tabs.addTab(checklists_widget, "Checklists")

        # Readmes tab
        readmes_widget = QWidget()
        readmes_layout = QVBoxLayout(readmes_widget)
        readmes_layout.addWidget(QLabel("Team Readmes"))
        readmes_layout.addWidget(QLabel("View and manage team documentation."))
        readmes_layout.addStretch()
        tabs.addTab(readmes_widget, "Readmes")

        # Forensic Q&A tab
        forensic_widget = QWidget()
        forensic_layout = QVBoxLayout(forensic_widget)
        forensic_layout.addWidget(QLabel("Forensic Questions"))
        forensic_layout.addWidget(QLabel("Ask and answer team questions."))
        forensic_layout.addStretch()
        tabs.addTab(forensic_widget, "Forensic Q&A")

        # Notes tab
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)
        notes_layout.addWidget(QLabel("Personal Notes"))
        notes_layout.addWidget(QLabel("Create and manage your private notes."))
        notes_layout.addStretch()
        tabs.addTab(notes_widget, "Notes")

        # Settings tab
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.addWidget(QLabel("Settings"))
        settings_layout.addWidget(QLabel("Configure server, database, and account settings."))
        settings_layout.addStretch()
        tabs.addTab(settings_widget, "Settings")

        main_layout.addWidget(tabs)
        main_layout.setContentsMargins(0, 0, 0, 0)

"""
Dashboard with clean, simple interface.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QPushButton
)
from PySide6.QtGui import QFont
from ..styles import STYLESHEET


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(STYLESHEET)
        self.init_ui()

    def init_ui(self):
        """Initialize dashboard."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)

        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title)

        logout_btn = QPushButton("Logout")
        logout_btn.setMaximumWidth(100)
        logout_btn.setObjectName("danger")
        header_layout.addStretch()
        header_layout.addWidget(logout_btn)

        header = QWidget()
        header.setLayout(header_layout)
        header.setStyleSheet("background-color: #1e40af;")
        main_layout.addWidget(header)

        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet(STYLESHEET)

        # Checklists
        checklists_widget = QWidget()
        checklists_layout = QVBoxLayout(checklists_widget)
        checklists_layout.addWidget(QLabel("Checklists"))
        checklists_layout.addWidget(QLabel("Manage and track team checklists."))
        checklists_layout.addStretch()
        tabs.addTab(checklists_widget, "Checklists")

        # Readmes
        readmes_widget = QWidget()
        readmes_layout = QVBoxLayout(readmes_widget)
        readmes_layout.addWidget(QLabel("Readmes"))
        readmes_layout.addWidget(QLabel("View team documentation."))
        readmes_layout.addStretch()
        tabs.addTab(readmes_widget, "Readmes")

        # Forensic Q&A
        forensic_widget = QWidget()
        forensic_layout = QVBoxLayout(forensic_widget)
        forensic_layout.addWidget(QLabel("Forensic Q&A"))
        forensic_layout.addWidget(QLabel("Ask and answer team questions."))
        forensic_layout.addStretch()
        tabs.addTab(forensic_widget, "Forensic Q&A")

        # Notes
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)
        notes_layout.addWidget(QLabel("Notes"))
        notes_layout.addWidget(QLabel("Manage personal notes."))
        notes_layout.addStretch()
        tabs.addTab(notes_widget, "Notes")

        # Settings
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.addWidget(QLabel("Settings"))
        settings_layout.addWidget(QLabel("Configure app settings."))
        settings_layout.addStretch()
        tabs.addTab(settings_widget, "Settings")

        main_layout.addWidget(tabs)

"""
Dashboard skeleton with placeholders for role-based sections:
- Checklists
- Readmes
- Forensic Questions
- Notes
- Settings
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Dashboard (role-based content will appear here)"))
        layout.addWidget(QLabel("Checklists, Readmes, Forensic Qs, Notes, Settings"))

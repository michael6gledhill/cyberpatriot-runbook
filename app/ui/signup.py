"""
Signup screen with clean, simple styling.
"""
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QLabel, QComboBox
)
from PySide6.QtGui import QFont
from ..auth import signup as do_signup
from ..styles import STYLESHEET


class SignupWidget(QWidget):
    goto_login = Signal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(STYLESHEET)
        self.init_ui()

    def init_ui(self):
        """Initialize UI with clean layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)
        main_layout.addStretch()

        # Title
        title = QLabel("Create Account")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1e40af;")
        main_layout.addWidget(title)

        # Name
        self.name = QLineEdit()
        self.name.setPlaceholderText("Full Name")
        self.name.setMinimumHeight(36)
        main_layout.addWidget(self.name)

        # Username
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setMinimumHeight(36)
        main_layout.addWidget(self.username)

        # Password
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        self.password.setMinimumHeight(36)
        main_layout.addWidget(self.password)

        # Role label
        role_label = QLabel("Role")
        role_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        main_layout.addWidget(role_label)

        # Role
        self.role = QComboBox()
        self.role.addItems(["admin", "coach", "team captain", "mentor", "competitor"])
        self.role.setMinimumHeight(36)
        main_layout.addWidget(self.role)

        # Team ID
        self.team_id = QLineEdit()
        self.team_id.setPlaceholderText("Team ID (optional)")
        self.team_id.setMinimumHeight(36)
        main_layout.addWidget(self.team_id)

        # Status
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(35)
        main_layout.addWidget(self.status)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.back_btn = QPushButton("Back")
        self.back_btn.setMinimumHeight(36)
        self.back_btn.setObjectName("secondary")
        button_layout.addWidget(self.back_btn)

        self.create_btn = QPushButton("Create")
        self.create_btn.setMinimumHeight(36)
        button_layout.addWidget(self.create_btn)

        main_layout.addLayout(button_layout)
        main_layout.addStretch()

        # Signals
        self.create_btn.clicked.connect(self.handle_signup)
        self.back_btn.clicked.connect(lambda: self.goto_login.emit())

    def handle_signup(self):
        """Process account creation."""
        try:
            team_val = int(self.team_id.text()) if self.team_id.text().strip() else None
        except ValueError:
            self.status.setStyleSheet("color: #dc2626; font-weight: bold;")
            self.status.setText("Team ID must be a number")
            return

        if not self.name.text().strip():
            self.status.setStyleSheet("color: #dc2626; font-weight: bold;")
            self.status.setText("Enter your name")
            return

        if not self.username.text().strip():
            self.status.setStyleSheet("color: #dc2626; font-weight: bold;")
            self.status.setText("Enter a username")
            return

        if not self.password.text():
            self.status.setStyleSheet("color: #dc2626; font-weight: bold;")
            self.status.setText("Enter a password")
            return

        try:
            uid = do_signup(
                self.name.text(),
                self.username.text(),
                self.password.text(),
                self.role.currentText(),
                team_val
            )
            self.status.setStyleSheet("color: #15803d; font-weight: bold;")
            self.status.setText("✓ Account created! Await approval.")
            self.name.clear()
            self.username.clear()
            self.password.clear()
            self.team_id.clear()
        except Exception as e:
            self.status.setStyleSheet("color: #dc2626; font-weight: bold;")
            self.status.setText(f"Error: {str(e)[:40]}")

"""
Signup screen with professional styling.
- Centered card layout
- Fields for name, username, password, role, team ID
- Create Account and Back buttons
- Status messaging
"""
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QLabel, QComboBox, QFrame, QScrollArea
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
        """Initialize UI with professional layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for smaller screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #f5f5f5; }")

        # Center the card
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.addStretch()

        # Card container
        card = QFrame()
        card.setMaximumWidth(420)
        card.setObjectName("card")
        card.setStyleSheet(
            card.styleSheet() + """
            QFrame#card {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            }
            """
        )

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)

        # Header
        title = QLabel("Create Account")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1e40af; margin-bottom: 4px;")
        card_layout.addWidget(title)

        subtitle = QLabel("Join your team on CyberPatriot Runbook")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666666; margin-bottom: 20px;")
        card_layout.addWidget(subtitle)

        # Name field
        self.name = QLineEdit()
        self.name.setPlaceholderText("Full Name")
        self.name.setMinimumHeight(40)
        self.name.setFont(QFont("Segoe UI", 11))
        card_layout.addWidget(self.name)

        # Username field
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setMinimumHeight(40)
        self.username.setFont(QFont("Segoe UI", 11))
        card_layout.addWidget(self.username)

        # Password field
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        self.password.setMinimumHeight(40)
        self.password.setFont(QFont("Segoe UI", 11))
        card_layout.addWidget(self.password)

        # Role field
        role_label = QLabel("Role")
        role_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        role_label.setStyleSheet("color: #1f2937;")
        card_layout.addWidget(role_label)

        self.role = QComboBox()
        self.role.addItems(["admin", "coach", "team captain", "mentor", "competitor"])
        self.role.setMinimumHeight(40)
        self.role.setFont(QFont("Segoe UI", 11))
        card_layout.addWidget(self.role)

        # Team ID field
        self.team_id = QLineEdit()
        self.team_id.setPlaceholderText("Team ID (optional)")
        self.team_id.setMinimumHeight(40)
        self.team_id.setFont(QFont("Segoe UI", 11))
        card_layout.addWidget(self.team_id)

        # Status label
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFont(QFont("Segoe UI", 10))
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(35)
        card_layout.addWidget(self.status)

        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Back button
        self.back_btn = QPushButton("Back")
        self.back_btn.setMinimumHeight(40)
        self.back_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.back_btn.setObjectName("secondary")
        self.back_btn.setStyleSheet(
            self.back_btn.styleSheet() + """
            QPushButton#secondary {
                background-color: #6b7280;
            }
            QPushButton#secondary:hover {
                background-color: #4b5563;
            }
            """
        )
        self.back_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.back_btn)

        # Create button
        self.create_btn = QPushButton("Create Account")
        self.create_btn.setMinimumHeight(40)
        self.create_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.create_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.create_btn)

        card_layout.addLayout(button_layout)

        # Wrap card
        card_container = QWidget()
        card_container_layout = QHBoxLayout(card_container)
        card_container_layout.addStretch()
        card_container_layout.addWidget(card)
        card_container_layout.addStretch()

        center_layout.addWidget(card_container)
        center_layout.addStretch()

        scroll.setWidget(center_widget)
        main_layout.addWidget(scroll)

        # Connect signals
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
            self.status.setText("Please enter your name")
            return

        if not self.username.text().strip():
            self.status.setStyleSheet("color: #dc2626; font-weight: bold;")
            self.status.setText("Please enter a username")
            return

        if not self.password.text():
            self.status.setStyleSheet("color: #dc2626; font-weight: bold;")
            self.status.setText("Please enter a password")
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
            self.status.setText(f"✓ Account created! Await approval to proceed.")
            # Clear fields
            self.name.clear()
            self.username.clear()
            self.password.clear()
            self.team_id.clear()
        except Exception as e:
            self.status.setStyleSheet("color: #dc2626; font-weight: bold;")
            self.status.setText(f"Error: {str(e)[:50]}")

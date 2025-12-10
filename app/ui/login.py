"""
Login screen with professional styling.
- Centered layout with brand header
- Username and password fields
- Login and Sign Up buttons
- Status messaging
"""
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QLabel, QFrame
)
from PySide6.QtGui import QFont
from ..auth import login as do_login
from ..styles import STYLESHEET


class LoginWidget(QWidget):
    goto_signup = Signal()
    goto_dashboard = Signal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(STYLESHEET)
        self.init_ui()

    def init_ui(self):
        """Initialize UI with professional layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Center the card vertically and horizontally
        center_layout = QVBoxLayout()
        center_layout.addStretch()

        # Card container
        card = QFrame()
        card.setMaximumWidth(400)
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
        card_layout.setSpacing(16)

        # Header
        title = QLabel("CyberPatriot Runbook")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1e40af; margin-bottom: 8px;")
        card_layout.addWidget(title)

        subtitle = QLabel("Team & Checklist Management")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666666; margin-bottom: 24px;")
        card_layout.addWidget(subtitle)

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

        # Status label
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFont(QFont("Segoe UI", 10))
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(30)
        card_layout.addWidget(self.status)

        # Login button
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setMinimumHeight(40)
        self.login_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_btn.setCursor(Qt.PointingHandCursor)
        card_layout.addWidget(self.login_btn)

        # Divider
        divider = QLabel("or")
        divider.setAlignment(Qt.AlignCenter)
        divider.setStyleSheet("color: #d1d5db; margin: 8px 0;")
        card_layout.addWidget(divider)

        # Signup button
        self.signup_btn = QPushButton("Create Account")
        self.signup_btn.setMinimumHeight(40)
        self.signup_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.signup_btn.setObjectName("secondary")
        self.signup_btn.setStyleSheet(
            self.signup_btn.styleSheet() + """
            QPushButton#secondary {
                background-color: #6b7280;
            }
            QPushButton#secondary:hover {
                background-color: #4b5563;
            }
            """
        )
        self.signup_btn.setCursor(Qt.PointingHandCursor)
        card_layout.addWidget(self.signup_btn)

        # Wrap card in a centered container
        card_container = QWidget()
        card_container_layout = QHBoxLayout(card_container)
        card_container_layout.addStretch()
        card_container_layout.addWidget(card)
        card_container_layout.addStretch()

        center_layout.addWidget(card_container)
        center_layout.addStretch()

        main_layout.addLayout(center_layout)

        # Connect signals
        self.login_btn.clicked.connect(self.handle_login)
        self.signup_btn.clicked.connect(lambda: self.goto_signup.emit())
        self.username.returnPressed.connect(self.handle_login)
        self.password.returnPressed.connect(self.handle_login)

    def handle_login(self):
        """Attempt login and show status."""
        user = do_login(self.username.text(), self.password.text())
        if not user:
            self.status.setObjectName("status-error")
            self.status.setStyleSheet("color: #dc2626; font-weight: bold;")
            self.status.setText("Invalid credentials")
            return
        if not user.get("approved"):
            self.status.setObjectName("status-info")
            self.status.setStyleSheet("color: #0284c7; font-weight: bold;")
            self.status.setText("Account pending approval")
            return
        self.status.setObjectName("status-success")
        self.status.setStyleSheet("color: #15803d; font-weight: bold;")
        self.status.setText(f"Welcome {user['name']}!")
        self.goto_dashboard.emit()

"""
Login screen with clean, simple styling.
"""
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QLabel
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
        """Initialize UI with clean layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        main_layout.addStretch()

        # Title
        title = QLabel("CyberPatriot Runbook")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1e40af;")
        main_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Team & Checklist Management")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666666; margin-bottom: 20px;")
        main_layout.addWidget(subtitle)

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

        # Status
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(30)
        main_layout.addWidget(self.status)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.login_btn = QPushButton("Sign In")
        self.login_btn.setMinimumHeight(36)
        self.login_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        button_layout.addWidget(self.login_btn)

        self.signup_btn = QPushButton("Sign Up")
        self.signup_btn.setMinimumHeight(36)
        self.signup_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.signup_btn.setObjectName("secondary")
        button_layout.addWidget(self.signup_btn)

        main_layout.addLayout(button_layout)
        main_layout.addStretch()

        # Signals
        self.login_btn.clicked.connect(self.handle_login)
        self.signup_btn.clicked.connect(lambda: self.goto_signup.emit())
        self.username.returnPressed.connect(self.handle_login)
        self.password.returnPressed.connect(self.handle_login)

    def handle_login(self):
        """Attempt login."""
        user = do_login(self.username.text(), self.password.text())
        if not user:
            self.status.setStyleSheet("color: #dc2626; font-weight: bold;")
            self.status.setText("Invalid credentials")
            return
        if not user.get("approved"):
            self.status.setStyleSheet("color: #0284c7; font-weight: bold;")
            self.status.setText("Account pending approval")
            return
        self.status.setStyleSheet("color: #15803d; font-weight: bold;")
        self.status.setText(f"Welcome {user['name']}!")
        self.goto_dashboard.emit()

"""
Login screen.
- Fields: username, password
- Buttons: Login, Signup
- Emits signals to switch screens or proceed to dashboard on success.
"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from ..auth import login as do_login


class LoginWidget(QWidget):
    goto_signup = Signal()
    goto_dashboard = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.info = QLabel("Login to CyberPatriot Runbook")
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        self.login_btn = QPushButton("Login")
        self.signup_btn = QPushButton("Sign Up")
        self.status = QLabel("")

        layout.addWidget(self.info)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.signup_btn)
        layout.addWidget(self.status)

        self.login_btn.clicked.connect(self.handle_login)
        self.signup_btn.clicked.connect(lambda: self.goto_signup.emit())

    def handle_login(self):
        user = do_login(self.username.text(), self.password.text())
        if not user:
            self.status.setText("Invalid credentials")
            return
        if not user.get("approved"):
            self.status.setText("Account pending approval")
            return
        self.status.setText(f"Welcome {user['name']} ({user['role']})")
        self.goto_dashboard.emit()

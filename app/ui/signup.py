"""
Signup screen.
- Fields: name, username, password, role, team ID (optional)
- Buttons: Create Account, Back to Login
- Enforces approval rules via `auth.signup`.
"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox
from ..auth import signup as do_signup


class SignupWidget(QWidget):
    goto_login = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.info = QLabel("Create an account")
        self.name = QLineEdit(); self.name.setPlaceholderText("Full Name")
        self.username = QLineEdit(); self.username.setPlaceholderText("Username")
        self.password = QLineEdit(); self.password.setEchoMode(QLineEdit.Password); self.password.setPlaceholderText("Password")
        self.role = QComboBox(); self.role.addItems(["admin","coach","team captain","mentor","competitor"])
        self.team_id = QLineEdit(); self.team_id.setPlaceholderText("Team ID (optional)")
        self.create_btn = QPushButton("Create Account")
        self.back_btn = QPushButton("Back to Login")
        self.status = QLabel("")

        for w in [self.info, self.name, self.username, self.password, self.role, self.team_id, self.create_btn, self.back_btn, self.status]:
            layout.addWidget(w)

        self.create_btn.clicked.connect(self.handle_signup)
        self.back_btn.clicked.connect(lambda: self.goto_login.emit())

    def handle_signup(self):
        try:
            team_val = int(self.team_id.text()) if self.team_id.text().strip() else None
        except ValueError:
            self.status.setText("Team ID must be a number")
            return
        uid = do_signup(self.name.text(), self.username.text(), self.password.text(), self.role.currentText(), team_val)
        self.status.setText(f"Account created (id={uid}). Await approval if required.")

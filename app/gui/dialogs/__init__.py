"""Dialog windows for CyberPatriot Runbook."""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QComboBox,
    QCheckBox,
    QMessageBox,
    QInputDialog,
)
from PySide6.QtCore import Qt


class ConfirmDialog(QDialog):
    """Generic confirmation dialog."""

    def __init__(self, parent=None, title: str = "Confirm", message: str = "Are you sure?"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 400, 150)
        self.result = False

        layout = QVBoxLayout()
        layout.addWidget(QLabel(message))

        button_layout = QHBoxLayout()
        yes_btn = QPushButton("Yes")
        no_btn = QPushButton("No")
        yes_btn.clicked.connect(self.accept)
        no_btn.clicked.connect(self.reject)
        button_layout.addWidget(yes_btn)
        button_layout.addWidget(no_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)


class PasswordDialog(QDialog):
    """Dialog for entering a password."""

    def __init__(self, parent=None, title: str = "Enter Password", prompt: str = "Password:"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 400, 120)
        self.password = None

        layout = QVBoxLayout()
        layout.addWidget(QLabel(prompt))

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self._handle_ok)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _handle_ok(self):
        """Handle OK button."""
        self.password = self.password_input.text()
        self.accept()

    def get_password(self) -> str:
        """Get entered password."""
        return self.password


class TextInputDialog(QDialog):
    """Dialog for entering text."""

    def __init__(
        self,
        parent=None,
        title: str = "Input",
        label: str = "Enter text:",
        default: str = "",
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 500, 150)
        self.text = None

        layout = QVBoxLayout()
        layout.addWidget(QLabel(label))

        self.text_input = QLineEdit()
        self.text_input.setText(default)
        layout.addWidget(self.text_input)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self._handle_ok)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _handle_ok(self):
        """Handle OK button."""
        self.text = self.text_input.text().strip()
        if not self.text:
            QMessageBox.warning(self, "Input Error", "Please enter some text.")
            return
        self.accept()

    def get_text(self) -> str:
        """Get entered text."""
        return self.text

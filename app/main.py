"""
Entry point for the PySide6 app.
Provides a basic stacked UI with Login, Signup, and Dashboard skeletons.
"""
from PySide6.QtWidgets import QApplication, QStackedWidget
import sys

from .ui.login import LoginWidget
from .ui.signup import SignupWidget
from .ui.dashboard import DashboardWidget
from .db import init_db


def build_app() -> QStackedWidget:
    """Initialize DB and construct the main stacked widget."""
    init_db()
    stack = QStackedWidget()

    login = LoginWidget()
    signup = SignupWidget()
    dashboard = DashboardWidget()

    stack.addWidget(login)      # index 0
    stack.addWidget(signup)     # index 1
    stack.addWidget(dashboard)  # index 2

    # Wire basic navigation signals
    login.goto_signup.connect(lambda: stack.setCurrentIndex(1))
    login.goto_dashboard.connect(lambda: stack.setCurrentIndex(2))
    signup.goto_login.connect(lambda: stack.setCurrentIndex(0))

    stack.setCurrentIndex(0)
    return stack


def main():
    app = QApplication(sys.argv)
    stack = build_app()
    stack.setWindowTitle("CyberPatriot Runbook")
    stack.resize(1000, 700)
    stack.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

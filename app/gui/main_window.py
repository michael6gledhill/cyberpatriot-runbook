"""Main window for CyberPatriot Runbook."""

from PySide6.QtWidgets import QStackedWidget, QWidget, QApplication
from PySide6.QtCore import Qt

from app.gui.login_window import LoginWindow
from app.gui.admin_dashboard import AdminDashboard
from app.gui.coach_dashboard import CoachDashboard
from app.gui.member_dashboard import MemberDashboard
from app.gui.competitor_dashboard import CompetitorDashboard
from app.gui.mentor_dashboard import MentorDashboard


class MainWindow(QStackedWidget):
    """Main application window that switches between login and dashboards."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberPatriot Runbook")
        self.setGeometry(100, 100, 1200, 700)

        # Create login window
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self._on_login_successful)

        # Add login window to stack
        self.addWidget(self.login_window)

        # Show login window first
        self.setCurrentWidget(self.login_window)

        self.current_dashboard = None

    def _on_login_successful(self, user_data: dict):
        """Handle successful login."""
        # Remove old dashboard if exists
        if self.current_dashboard:
            self.removeWidget(self.current_dashboard)
            self.current_dashboard.close()
            self.current_dashboard = None

        # Create appropriate dashboard based on role
        role = user_data["role"].lower()
        if role == "admin":
            self.current_dashboard = AdminDashboard(user_data)
        elif role == "coach":
            self.current_dashboard = CoachDashboard(user_data)
        elif role == "captain":
            self.current_dashboard = MemberDashboard(user_data)
        elif role == "competitor":
            self.current_dashboard = CompetitorDashboard(user_data)
        elif role == "mentor":
            self.current_dashboard = MentorDashboard(user_data)
        else:
            self.current_dashboard = MemberDashboard(user_data)

        # Connect logout signal
        self.current_dashboard.user_logged_out.connect(self._on_user_logged_out)

        # Add dashboard to stack and switch to it
        self.addWidget(self.current_dashboard)
        self.setCurrentWidget(self.current_dashboard)

    def _on_user_logged_out(self):
        """Handle user logout."""
        # Remove and close current dashboard
        if self.current_dashboard:
            self.removeWidget(self.current_dashboard)
            self.current_dashboard.close()
            self.current_dashboard = None

        # Switch back to login window
        self.setCurrentWidget(self.login_window)
        self.login_window.login_email.setFocus()

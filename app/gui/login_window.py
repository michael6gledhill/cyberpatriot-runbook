"""Login window for CyberPatriot Runbook application."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QComboBox,
    QMessageBox,
    QTabWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.database.repositories import UserRepository, TeamRepository
from app.security import PasswordManager


class LoginWindow(QMainWindow):
    """Main login window with login and signup tabs."""

    login_successful = Signal(dict)  # Emits user data on successful login

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberPatriot Runbook - Login")
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet(self._get_stylesheet())

        # Create central widget with tabs
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.tab_widget = QTabWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(layout)

        # Create login and signup tabs
        self.login_tab = self._create_login_tab()
        self.signup_tab = self._create_signup_tab()

        self.tab_widget.addTab(self.login_tab, "Login")
        self.tab_widget.addTab(self.signup_tab, "Sign Up")

    def _create_login_tab(self) -> QWidget:
        """Create the login tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Login to Your Account")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Email field
        layout.addWidget(QLabel("Email:"))
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Enter your email")
        layout.addWidget(self.login_email)

        # Password field
        layout.addWidget(QLabel("Password:"))
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter your password")
        self.login_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.login_password)

        # Login button
        login_button = QPushButton("Login")
        login_button.setMinimumHeight(40)
        login_button.clicked.connect(self._handle_login)
        layout.addWidget(login_button)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _create_signup_tab(self) -> QWidget:
        """Create the signup tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Create a New Account")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Name field
        layout.addWidget(QLabel("Full Name:"))
        self.signup_name = QLineEdit()
        self.signup_name.setPlaceholderText("Enter your full name")
        layout.addWidget(self.signup_name)

        # Email field
        layout.addWidget(QLabel("Email:"))
        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("Enter your email")
        layout.addWidget(self.signup_email)

        # Password field
        layout.addWidget(QLabel("Password:"))
        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("Enter a strong password")
        self.signup_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.signup_password)

        # Confirm password field
        layout.addWidget(QLabel("Confirm Password:"))
        self.signup_confirm = QLineEdit()
        self.signup_confirm.setPlaceholderText("Confirm your password")
        self.signup_confirm.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.signup_confirm)

        # Role selection
        layout.addWidget(QLabel("Requested Role:"))
        self.signup_role = QComboBox()
        self.signup_role.addItems(["Member", "Captain", "Coach"])
        layout.addWidget(self.signup_role)

        # Team ID field
        layout.addWidget(QLabel("Team ID (format: NN-NNNN):"))
        self.signup_team_id = QLineEdit()
        self.signup_team_id.setPlaceholderText("e.g., 12-3456")
        layout.addWidget(self.signup_team_id)

        # Signup button
        signup_button = QPushButton("Sign Up")
        signup_button.setMinimumHeight(40)
        signup_button.clicked.connect(self._handle_signup)
        layout.addWidget(signup_button)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _handle_login(self):
        """Handle login button click."""
        email = self.login_email.text().strip()
        password = self.login_password.text()

        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both email and password.")
            return

        try:
            user = UserRepository.get_user_by_email(email)

            if not user:
                QMessageBox.warning(self, "Login Failed", "User not found.")
                return

            if not PasswordManager.verify_password(password, user.password_hash):
                QMessageBox.warning(self, "Login Failed", "Invalid password.")
                return

            if not user.is_active:
                QMessageBox.warning(self, "Account Inactive", "Your account has been deactivated.")
                return

            # Check if user is approved (except for admins)
            if user.role.value != "admin" and not user.is_approved:
                QMessageBox.warning(
                    self,
                    "Pending Approval",
                    "Your account is pending admin approval. Please wait for your team captain to approve your access.",
                )
                return

            # Successful login
            user_data = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.value,
                "team_id": user.team_id,
                "is_approved": user.is_approved,
            }

            self.login_successful.emit(user_data)
            self.login_email.clear()
            self.login_password.clear()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during login: {str(e)}")

    def _handle_signup(self):
        """Handle signup button click."""
        name = self.signup_name.text().strip()
        email = self.signup_email.text().strip()
        password = self.signup_password.text()
        confirm = self.signup_confirm.text()
        role = self.signup_role.currentText().lower()
        team_id_str = self.signup_team_id.text().strip()

        # Validation
        if not all([name, email, password, confirm, team_id_str]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        if password != confirm:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 8 characters long.")
            return

        # Check if email already exists
        existing_user = UserRepository.get_user_by_email(email)
        if existing_user:
            QMessageBox.warning(self, "Email Exists", "An account with this email already exists.")
            return

        # Verify team ID exists
        team = TeamRepository.get_team_by_team_id(team_id_str)
        if not team:
            QMessageBox.warning(self, "Team Not Found", f"Team ID '{team_id_str}' does not exist.")
            return

        try:
            # Hash password
            password_hash = PasswordManager.hash_password(password)

            # Create user (pending approval)
            new_user = UserRepository.create_user(
                name=name, email=email, password_hash=password_hash, team_id=team.id, role=role
            )

            QMessageBox.information(
                self,
                "Account Created",
                f"Your account has been created and is pending approval.\n"
                f"Your team captain will review your request.",
            )

            # Clear fields
            self.signup_name.clear()
            self.signup_email.clear()
            self.signup_password.clear()
            self.signup_confirm.clear()
            self.signup_team_id.clear()

            # Switch to login tab
            self.tab_widget.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during signup: {str(e)}")

    def _get_stylesheet(self) -> str:
        """Return the stylesheet for the login window."""
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QLabel {
            color: #333333;
            font-weight: bold;
        }
        QLineEdit {
            padding: 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: white;
        }
        QLineEdit:focus {
            border: 2px solid #4CAF50;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 4px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        QComboBox {
            padding: 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: white;
        }
        QTabWidget::pane {
            border: 1px solid #cccccc;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            color: #333333;
            padding: 8px 20px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #4CAF50;
            color: white;
        }
        """

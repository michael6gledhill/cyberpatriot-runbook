"""Login window for CyberPatriot Runbook application."""

import sys
import hashlib
from PySide6.QtWidgets import (
    QApplication,
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

from db_config import get_connection, close_connection


class PasswordManager:
    """Utility class for password hashing and verification."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return PasswordManager.hash_password(password) == password_hash


class UserRepository:
    """Repository for user database operations."""
    
    @staticmethod
    def get_user_by_username(username: str) -> dict | None:
        """Get user by username from database."""
        connection = get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, name, username, password_hash, is_active FROM users WHERE username = %s",
                (username,)
            )
            result = cursor.fetchone()
            cursor.close()
            return result
        finally:
            close_connection(connection)
    
    @staticmethod
    def get_user_by_id(user_id: int) -> dict | None:
        """Get user by ID from database."""
        connection = get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, name, username, is_active FROM users WHERE id = %s",
                (user_id,)
            )
            result = cursor.fetchone()
            cursor.close()
            return result
        finally:
            close_connection(connection)
    
    @staticmethod
    def username_exists(username: str) -> bool:
        """Check if a username already exists."""
        connection = get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            exists = cursor.fetchone() is not None
            cursor.close()
            return exists
        finally:
            close_connection(connection)
    
    @staticmethod
    def create_user(name: str, username: str, password_hash: str, role: str = "competitor", team_id: int | None = None) -> dict | None:
        """Create a new user in the database."""
        connection = get_connection()
        if not connection:
            return None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Insert user
            cursor.execute(
                """
                INSERT INTO users (name, username, password_hash, email, is_active)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (name, username, password_hash, f"{username}@cyberpatriot.local", True)
            )
            user_id = cursor.lastrowid
            
            # Ensure roles exist
            roles = ['admin', 'coach', 'team_captain', 'mentor', 'competitor']
            for r in roles:
                cursor.execute("SELECT id FROM roles WHERE name = %s", (r,))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO roles (name) VALUES (%s)", (r,))
            
            # Get role ID
            cursor.execute("SELECT id FROM roles WHERE name = %s", (role,))
            role_result = cursor.fetchone()
            role_id = int(role_result['id']) if role_result else 1
            
            # Create team membership
            if role in ['admin', 'coach']:
                status = 'approved'
                # Try to use team_id=1 if it exists, otherwise use the provided team_id or 1
                if team_id:
                    pass  # Use provided team_id
                else:
                    # Check if team 1 exists
                    cursor.execute("SELECT id FROM teams WHERE id = 1")
                    if cursor.fetchone():
                        team_id = 1
                    else:
                        # Create a default team if it doesn't exist
                        cursor.execute(
                            """
                            INSERT INTO teams (name, team_code, division, created_by_user_id)
                            VALUES (%s, %s, %s, %s)
                            """,
                            ('Default Team', '00-0000', 'Open', user_id)
                        )
                        team_id = cursor.lastrowid
            else:
                status = 'pending'
                if not team_id:
                    raise ValueError("Team ID required for non-admin/coach roles")
            
            # Only insert team_members if team_id is valid
            if team_id:
                cursor.execute(
                    """
                    INSERT INTO team_members (user_id, team_id, role_id, status)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, team_id, role_id, status)
                )
            else:
                raise ValueError("No valid team_id for team membership")
            
            connection.commit()
            
            return {
                'id': user_id,
                'name': name,
                'username': username,
                'role': role,
                'team_id': team_id,
                'is_approved': (status == 'approved')
            }
        except Exception as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            close_connection(connection)


class TeamRepository:
    """Repository for team database operations."""
    
    @staticmethod
    def get_team_by_id(team_id: int):
        """Get team by ID from database."""
        connection = get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, name, team_code FROM teams WHERE id = %s",
                (team_id,)
            )
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'team_code': result[2]
                }
            return None
        finally:
            close_connection(connection)


class LoginWindow(QMainWindow):
    """Main login window with login and signup tabs."""

    login_successful = Signal(dict)  # Emits user data on successful login

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberPatriot Runbook - Authentication")
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

        # Username field
        layout.addWidget(QLabel("Username:"))
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Enter your username")
        layout.addWidget(self.login_username)

        # Password field
        layout.addWidget(QLabel("Password:"))
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter your password")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.login_password)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(40)
        self.login_button.setDefault(True)  # Pressing Enter triggers login
        self.login_button.clicked.connect(self._handle_login)
        # Hitting Enter in either field triggers the login button
        self.login_username.returnPressed.connect(self.login_button.click)
        self.login_password.returnPressed.connect(self.login_button.click)
        layout.addWidget(self.login_button)

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

        # Account type selection (dropdown)
        layout.addWidget(QLabel("Account Type:"))
        self.signup_role = QComboBox()
        self.signup_role.addItems(["Competitor", "Team Captain", "Coach", "Mentor", "Admin"])
        self.signup_role.currentTextChanged.connect(self._on_role_changed)
        layout.addWidget(self.signup_role)

        # Name field
        layout.addWidget(QLabel("Full Name:"))
        self.signup_name = QLineEdit()
        self.signup_name.setPlaceholderText("Enter your full name")
        layout.addWidget(self.signup_name)

        # Username field
        layout.addWidget(QLabel("Username:"))
        self.signup_username = QLineEdit()
        self.signup_username.setPlaceholderText("Enter your username (alphanumeric)")
        layout.addWidget(self.signup_username)

        # Password field
        layout.addWidget(QLabel("Password:"))
        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("Enter a strong password (min 8 characters)")
        self.signup_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.signup_password)

        # Confirm password field
        layout.addWidget(QLabel("Confirm Password:"))
        self.signup_confirm = QLineEdit()
        self.signup_confirm.setPlaceholderText("Confirm your password")
        self.signup_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.signup_confirm)

        # Team ID field (hidden for admin/mentor on signup)
        layout.addWidget(QLabel("Team ID:"))
        self.signup_team_id = QLineEdit()
        self.signup_team_id.setPlaceholderText("Required for Competitor, Team Captain (enter numeric ID)")
        self.signup_team_id_label = layout.itemAt(layout.count() - 2).widget()
        layout.addWidget(self.signup_team_id)

        # Signup button
        signup_button = QPushButton("Sign Up")
        signup_button.setMinimumHeight(40)
        signup_button.clicked.connect(self._handle_signup)
        layout.addWidget(signup_button)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _on_role_changed(self):
        """Update UI when role selection changes."""
        role = self.signup_role.currentText().lower()
        requires_team = role in ["competitor", "team captain"]
        self.signup_team_id.setEnabled(requires_team)
        self.signup_team_id.setPlaceholderText(
            "Enter team ID (numeric)" if requires_team else "Not required for this role"
        )

    def _handle_login(self):
        """Handle login button click."""
        username = self.login_username.text().strip()
        password = self.login_password.text()

        if not username or not password:
            self._show_message("Input Error", "Please enter both username and password.", QMessageBox.Icon.Warning)
            return

        try:
            user = UserRepository.get_user_by_username(username)

            if not user:
                self._show_message("Login Failed", "User not found.", QMessageBox.Icon.Warning)
                return

            if not PasswordManager.verify_password(password, user['password_hash']):
                self._show_message("Login Failed", "Invalid password.", QMessageBox.Icon.Warning)
                return

            if not user['is_active']:
                self._show_message("Account Inactive", "Your account has been deactivated.", QMessageBox.Icon.Warning)
                return

            # Get user role and approval status
            connection = get_connection()
            if not connection:
                self._show_message("Error", "Cannot connect to database.", QMessageBox.Icon.Critical)
                return

            try:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    SELECT r.name, tm.status 
                    FROM team_members tm
                    JOIN roles r ON tm.role_id = r.id
                    WHERE tm.user_id = %s
                    LIMIT 1
                    """,
                    (user['id'],)
                )
                role_result = cursor.fetchone()
                cursor.close()

                if role_result:
                    role, approval_status = role_result
                    is_approved = (approval_status == 'approved')

                    # Check if user is approved (except for admins)
                    if role != "admin" and not is_approved:
                        pending_msg = "Your account is pending admin approval. "
                        if role == "coach":
                            pending_msg += "Please wait for an admin to approve your access."
                        else:
                            pending_msg += "Please wait for your team captain to approve your access."
                        self._show_message(
                            "Pending Approval",
                            pending_msg,
                            QMessageBox.Icon.Warning,
                        )
                        return

                    # Successful login
                    user_data = {
                        "id": user['id'],
                        "name": user['name'],
                        "username": user['username'],
                        "role": role,
                        "is_approved": is_approved,
                    }

                    self.login_successful.emit(user_data)
                    self.login_username.clear()
                    self.login_password.clear()
            finally:
                close_connection(connection)

        except Exception as e:
            self._show_message("Error", f"An error occurred during login: {str(e)}", QMessageBox.Icon.Critical)

    def _validate_team_code(self, team_code: str) -> tuple[bool, str]:
        """Validate team code format (XX-XXXX where X is digit)."""
        import re
        # Pattern: 2 digits, dash, 4 digits (e.g., 00-0000)
        pattern = r'^\d{2}-\d{4}$'
        if not re.match(pattern, team_code):
            return False, "Team code must be in format: XX-XXXX (e.g., 00-0000)"
        return True, ""
    
    def _get_team_by_code(self, team_code: str) -> dict | None:
        """Get team by team code from database."""
        connection = get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, name, team_code FROM teams WHERE team_code = %s",
                (team_code,)
            )
            result = cursor.fetchone()
            cursor.close()
            return result
        finally:
            close_connection(connection)

    def _show_message(self, title: str, message: str, icon: QMessageBox.Icon = QMessageBox.Icon.Information):
        """Show a message box with selectable text."""
        box = QMessageBox(self)
        box.setIcon(icon)
        box.setWindowTitle(title)
        box.setText(message)
        box.exec()

    def _handle_signup(self):
        """Handle signup button click."""
        name = self.signup_name.text().strip()
        username = self.signup_username.text().strip()
        password = self.signup_password.text()
        confirm = self.signup_confirm.text()
        team_id_str = self.signup_team_id.text().strip()

        # Get selected account type from dropdown
        role_display = self.signup_role.currentText().lower()

        # Map display names to role values
        role_map = {
            "competitor": "competitor",
            "team captain": "team_captain",
            "coach": "coach",
            "mentor": "mentor",
            "admin": "admin"
        }
        role_str = role_map.get(role_display, "competitor")

        # Validation
        if not all([name, username, password, confirm]):
            self._show_message("Input Error", "Please fill in all required fields.", QMessageBox.Icon.Warning)
            return

        if password != confirm:
            self._show_message("Password Mismatch", "Passwords do not match.", QMessageBox.Icon.Warning)
            return

        if len(password) < 8:
            self._show_message("Weak Password", "Password must be at least 8 characters long.", QMessageBox.Icon.Warning)
            return

        # Check if username already exists
        if UserRepository.username_exists(username):
            self._show_message("Username Exists", "This username is already taken.", QMessageBox.Icon.Warning)
            return

        # For competitor/team_captain users, team code is required
        team = None
        if role_str in ["competitor", "team_captain"]:
            if not team_id_str:
                self._show_message("Team Required", "Team code is required for this role.", QMessageBox.Icon.Warning)
                return

            # Validate team code format
            is_valid, error_msg = self._validate_team_code(team_id_str)
            if not is_valid:
                self._show_message("Invalid Format", error_msg, QMessageBox.Icon.Warning)
                return
            
            # Check if team exists by team code
            team = self._get_team_by_code(team_id_str)
            if not team:
                self._show_message("Team Not Found", f"Team code '{team_id_str}' does not exist.", QMessageBox.Icon.Warning)
                return

        try:
            # Hash password
            password_hash = PasswordManager.hash_password(password)

            # Create user
            new_user = UserRepository.create_user(
                name=name,
                username=username,
                password_hash=password_hash,
                role=role_str,
                team_id=int(team['id']) if team else None
            )

            if new_user:
                if role_str in ['admin', 'coach', 'mentor']:
                    message = (
                        f"Your {role_display.capitalize()} account has been created successfully!\n"
                        f"You can now log in with your credentials."
                    )
                    self._show_message("Account Created", message, QMessageBox.Icon.Information)
                    # Auto-login admin/coach/mentor
                    user_data = {
                        "id": new_user['id'],
                        "name": new_user['name'],
                        "username": new_user['username'],
                        "role": new_user['role'],
                        "is_approved": new_user['is_approved'],
                    }
                    self.login_successful.emit(user_data)
                else:
                    message = (
                        "Your account has been created and is pending approval.\n"
                    "Your team coach will review your request soon."
                )
                self._show_message("Account Created", message, QMessageBox.Icon.Information)

            # Clear fields
            self.signup_name.clear()
            self.signup_username.clear()
            self.signup_password.clear()
            self.signup_confirm.clear()
            self.signup_team_id.clear()

            # Switch to login tab if not auto-logged in
            if role_str not in ["admin", "coach", "mentor"]:
                self.tab_widget.setCurrentIndex(0)

        except Exception as e:
            self._show_message("Error", f"An error occurred during signup: {str(e)}", QMessageBox.Icon.Critical)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())

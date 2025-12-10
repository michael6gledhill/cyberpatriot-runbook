"""Login window for CyberPatriot Runbook application."""

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

from app.database.repositories import UserRepository, TeamRepository
from app.models.user import UserRole
from app.security import PasswordManager
from app.gui.dialogs.settings_dialog import SettingsDialog
from app.database import init_db
import os


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

        # Top bar with Settings button
        top_bar = QHBoxLayout()
        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self._open_settings)
        top_bar.addStretch()
        top_bar.addWidget(settings_btn)
        layout.addLayout(top_bar)

        # Create login and signup tabs
        self.login_tab = self._create_login_tab()
        self.signup_tab = self._create_signup_tab()

        self.tab_widget.addTab(self.login_tab, "Login")
        self.tab_widget.addTab(self.signup_tab, "Sign Up")
        # Documentation tab
        self.docs_tab = self._create_docs_tab()
        self.tab_widget.addTab(self.docs_tab, "Documentation")

    def _open_settings(self):
        """Open settings dialog to configure backend connection."""
        # Prefill from environment if present
        current_url = os.getenv("DATABASE_URL", "")
        dlg = SettingsDialog(self, current_url)
        if dlg.exec():
            new_url = dlg.get_database_url()
            # Persist to .env in repo root
            try:
                env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                        ".env")
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(f"DATABASE_URL={new_url}\n")
                os.environ["DATABASE_URL"] = new_url
                init_db(new_url)
                QMessageBox.information(self, "Settings Saved", "Backend connection updated and saved.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

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
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(40)
        self.login_button.setDefault(True)  # Pressing Enter triggers login
        self.login_button.clicked.connect(self._handle_login)
        # Hitting Enter in either field triggers the login button
        self.login_email.returnPressed.connect(self.login_button.click)
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
        self.signup_role.addItems(["Competitor", "Captain", "Coach", "Mentor", "Admin"])
        layout.addWidget(self.signup_role)

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

        # Team ID field (hidden for admin/mentor on signup)
        layout.addWidget(QLabel("Team ID (format: NN-NNNN):"))
        self.signup_team_id = QLineEdit()
        self.signup_team_id.setPlaceholderText("e.g., 12-3456 (optional for Coach/Mentor/Admin)")
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
            self._show_message("Input Error", "Please enter both email and password.", QMessageBox.Warning)
            return

        try:
            user = UserRepository.get_user_by_email(email)

            if not user:
                self._show_message("Login Failed", "User not found.", QMessageBox.Warning)
                return

            if not PasswordManager.verify_password(password, user.password_hash):
                self._show_message("Login Failed", "Invalid password.", QMessageBox.Warning)
                return

            if not user.is_active:
                self._show_message("Account Inactive", "Your account has been deactivated.", QMessageBox.Warning)
                return

            # Check if user is approved (except for admins)
            if user.role != "admin" and not user.is_approved:
                pending_msg = "Your account is pending admin approval. "
                if user.role == "coach":
                    pending_msg += "Please wait for an admin to approve your access."
                else:
                    pending_msg += "Please wait for your team captain to approve your access."
                self._show_message(
                    "Pending Approval",
                    pending_msg,
                    QMessageBox.Warning,
                )
                return

            # Successful login
            user_data = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "team_id": user.team_id,
                "is_approved": user.is_approved,
            }

            self.login_successful.emit(user_data)
            self.login_email.clear()
            self.login_password.clear()

        except Exception as e:
            self._show_message("Error", f"An error occurred during login: {str(e)}", QMessageBox.Critical)

    def _show_message(self, title: str, message: str, icon: QMessageBox.Icon = QMessageBox.Information):
        """Show a message box with selectable text and a copy button."""
        box = QMessageBox(self)
        box.setIcon(icon)
        box.setWindowTitle(title)
        box.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        box.setText(message)

        copy_btn = box.addButton("Copy", QMessageBox.ActionRole)
        ok_btn = box.addButton(QMessageBox.Ok)
        box.setDefaultButton(ok_btn)
        box.exec()

        if box.clickedButton() == copy_btn:
            QApplication.clipboard().setText(message)

    def _handle_signup(self):
        """Handle signup button click."""
        name = self.signup_name.text().strip()
        email = self.signup_email.text().strip()
        password = self.signup_password.text()
        confirm = self.signup_confirm.text()
        team_id_str = self.signup_team_id.text().strip()

        # Get selected account type from dropdown
        role_display = self.signup_role.currentText().lower()
        
        # Map display names to role enum values
        role_map = {
            "competitor": "member",
            "captain": "captain",
            "coach": "coach",
            "mentor": "coach",  # Mentor maps to coach role
            "admin": "admin"
        }
        role_str = role_map.get(role_display, "member")

        # Validation
        if not all([name, email, password, confirm]):
            self._show_message("Input Error", "Please fill in all required fields.", QMessageBox.Warning)
            return

        if password != confirm:
            self._show_message("Password Mismatch", "Passwords do not match.", QMessageBox.Warning)
            return

        if len(password) < 8:
            self._show_message("Weak Password", "Password must be at least 8 characters long.", QMessageBox.Warning)
            return

        # Check if email already exists
        existing_user = UserRepository.get_user_by_email(email)
        if existing_user:
            self._show_message("Email Exists", "An account with this email already exists.", QMessageBox.Warning)
            return

        # For competitor/captain users, team ID is required
        team = None
        if role_str in ["member", "captain"]:
            if not team_id_str:
                self._show_message("Team Required", "Team ID is required for competitors and captains.", QMessageBox.Warning)
                return
            
            # Verify team ID exists
            team = TeamRepository.get_team_by_team_id(team_id_str)
            if not team:
                self._show_message("Team Not Found", f"Team ID '{team_id_str}' does not exist.", QMessageBox.Warning)
                return

        try:
            # Hash password
            password_hash = PasswordManager.hash_password(password)

            # Convert string role to UserRole enum
            role_enum = UserRole(role_str)

            # Create user
            new_user = UserRepository.create_user(
                name=name,
                email=email,
                password_hash=password_hash,
                team_id=team.id if team else None,
                role=role_enum
            )

            if role_str in ["admin", "coach"]:
                message = (
                    f"Your {role_display.capitalize()} account has been created successfully!\n"
                    f"You can now log in and create teams."
                )
                self._show_message("Account Created", message, QMessageBox.Information)
                # Auto-login admin/coach/mentor
                user_data = {
                    "id": new_user.id,
                    "name": new_user.name,
                    "email": new_user.email,
                    "role": new_user.role if isinstance(new_user.role, str) else new_user.role.value,
                    "team_id": new_user.team_id,
                    "is_approved": new_user.is_approved,
                }
                self.login_successful.emit(user_data)
            else:
                message = (
                    "Your account has been created and is pending approval.\n"
                    "Your team coach will review your request soon."
                )
                self._show_message("Account Created", message, QMessageBox.Information)

            # Clear fields
            self.signup_name.clear()
            self.signup_email.clear()
            self.signup_password.clear()
            self.signup_confirm.clear()
            self.signup_team_id.clear()

            # Switch to login tab if not auto-logged in
            if role_str not in ["admin", "coach"]:
                self.tab_widget.setCurrentIndex(0)

        except Exception as e:
            self._show_message("Error", f"An error occurred during signup: {str(e)}", QMessageBox.Critical)

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

    def _create_docs_tab(self) -> QWidget:
        """Create a documentation tab with a thorough, concise overview."""
        from PySide6.QtWidgets import QTextEdit
        widget = QWidget()
        layout = QVBoxLayout()
        doc = QTextEdit()
        doc.setReadOnly(True)
        doc.setMinimumHeight(400)
        # Load bundled docs if available; fallback to embedded summary
        content = self._get_embedded_docs()
        doc.setText(content)
        layout.addWidget(doc)
        widget.setLayout(layout)
        return widget

    def _get_embedded_docs(self) -> str:
        """Return a concise, comprehensive app overview for AI prompts."""
        return (
            "CyberPatriot Runbook — Architecture & Usage\n\n"
            "Purpose: Desktop GUI to manage teams, checklists, docs, notes; MySQL backend.\n\n"
            "Stack: PySide6 GUI; SQLAlchemy ORM; Alembic migrations; PyMySQL; bcrypt; dotenv.\n\n"
            "Data Model: Users (member/captain/coach/admin), Teams (creator, members),\n"
            "Checklists (items, status per user), READMEs (per team), Notes (encrypted),\n"
            "AuditLog (actions), JoinRequests (requester->team creator).\n\n"
            "Config: DATABASE_URL via .env or Settings (Login page).\n"
            "Backend: MySQL 8 via Docker on Ubuntu; port 3306; user cp_user.\n\n"
            "Auth: PasswordManager (bcrypt); roles gate dashboards.\n\n"
            "Dashboards:\n"
            "- Admin: Team management; user approvals; member management (delete/change role); audit log.\n"
            "- Coach: My teams; team members; join requests; activity log; create team auto-adds coach.\n"
            "- Captain: Checklists/READMEs/Notes; Team Members (approve competitors); Join Requests.\n"
            "- Member/Competitor: Checklists/READMEs/Notes; Join Requests.\n\n"
            "Key Flows:\n"
            "- Settings: Set backend DB (host, port, user, pass, db). Saves to .env and re-inits DB.\n"
            "- Signup: Admin/Coach auto-login; competitors/captains pending approval by coach/captain.\n"
            "- Approvals: Admin/Coach/Captain can approve via respective tabs; repositories handle updates.\n"
            "- Team creation: TeamRepository.create_team assigns creating coach to team, approves.\n\n"
            "Repositories: app/database/repositories.py exposes CRUD for Users, Teams, Checklists, READMEs, Notes,\n"
            "Audit logs, Join requests. Use get_session() for transactions; methods commit/rollback.\n\n"
            "Migrations: Alembic uses DATABASE_URL; run `alembic upgrade head`.\n"
            "Docs: See docs/backend-ubuntu.md for Docker setup; README quick-start included.\n\n"
            "To recreate via AI: Request a PySide6 multi-dashboard app with SQLAlchemy models above,\n"
            "repositories pattern, Alembic migration, and a Settings dialog to set DATABASE_URL;\n"
            "dashboards per role with tab layouts and table actions described; include bcrypt auth and audit logging.\n"
        )

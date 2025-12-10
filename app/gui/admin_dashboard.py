"""Admin dashboard for CyberPatriot Runbook."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QDialog,
    QLabel,
    QLineEdit,
    QComboBox,
    QMessageBox,
    QHeaderView,
    QSpinBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.database.repositories import (
    UserRepository,
    TeamRepository,
    AuditLogRepository,
)
from app.security import PasswordManager


class AdminDashboard(QMainWindow):
    """Main admin dashboard window."""

    user_logged_out = Signal()

    def __init__(self, admin_user: dict):
        super().__init__()
        self.admin_user = admin_user
        self.setWindowTitle(f"CyberPatriot Runbook - Admin Dashboard ({admin_user['name']})")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(self._get_stylesheet())

        # Create central widget with tabs
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        # Top bar with logout button
        top_bar = self._create_top_bar()
        layout.addLayout(top_bar)

        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        self.team_tab = self._create_team_management_tab()
        self.approval_tab = self._create_user_approval_tab()
        self.member_tab = self._create_member_management_tab()
        self.audit_tab = self._create_audit_log_tab()

        self.tab_widget.addTab(self.team_tab, "Team Management")
        self.tab_widget.addTab(self.approval_tab, "User Approvals")
        self.tab_widget.addTab(self.member_tab, "Member Management")
        self.tab_widget.addTab(self.audit_tab, "Activity Log")

        layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(layout)

    def _create_top_bar(self) -> QHBoxLayout:
        """Create the top navigation bar."""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        welcome_label = QLabel(f"Welcome, {self.admin_user['name']} (Admin)")
        layout.addWidget(welcome_label)
        layout.addStretch()

        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self._handle_logout)
        layout.addWidget(logout_button)

        return layout

    def _create_team_management_tab(self) -> QWidget:
        """Create team management tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Team Management")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        layout.addWidget(title)

        # Teams table
        self.teams_table = QTableWidget()
        self.teams_table.setColumnCount(5)
        self.teams_table.setHorizontalHeaderLabels(["Team Name", "Team ID", "Division", "Members", "Actions"])
        self._refresh_teams_table()
        layout.addWidget(self.teams_table)

        # Buttons
        button_layout = QHBoxLayout()
        create_button = QPushButton("Create Team")
        create_button.clicked.connect(self._show_create_team_dialog)
        button_layout.addWidget(create_button)

        edit_button = QPushButton("Edit Selected")
        edit_button.clicked.connect(self._show_edit_team_dialog)
        button_layout.addWidget(edit_button)

        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self._handle_delete_team)
        button_layout.addWidget(delete_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def _create_user_approval_tab(self) -> QWidget:
        """Create user approval tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Pending User Approvals")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        layout.addWidget(title)

        # Pending users table
        self.pending_table = QTableWidget()
        self.pending_table.setColumnCount(6)
        self.pending_table.setHorizontalHeaderLabels(
            ["Name", "Email", "Requested Role", "Team", "Applied", "Actions"]
        )
        self._refresh_pending_users_table()
        layout.addWidget(self.pending_table)

        # Buttons
        button_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._refresh_pending_users_table)
        button_layout.addWidget(refresh_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def _create_member_management_tab(self) -> QWidget:
        """Create member management tab with search."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Team Member Management")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        layout.addWidget(title)

        # Search bar
        search_layout = QHBoxLayout()
        self.member_search_box = QLineEdit()
        self.member_search_box.setPlaceholderText("Search by name, email, team, or role...")
        self.member_search_box.textChanged.connect(self._filter_members_table)
        search_layout.addWidget(self.member_search_box)
        layout.addLayout(search_layout)

        # Members table
        self.members_table = QTableWidget()
        self.members_table.setColumnCount(5)
        self.members_table.setHorizontalHeaderLabels(["Name", "Email", "Team", "Role", "Actions"])
        self._refresh_members_table()
        layout.addWidget(self.members_table)

        # Buttons
        button_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._refresh_members_table)
        button_layout.addWidget(refresh_button)

        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self._handle_remove_member)
        button_layout.addWidget(remove_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def _filter_members_table(self):
        """Filter members table based on search box input."""
        search_text = self.member_search_box.text().lower()
        for row in range(self.members_table.rowCount()):
            match = False
            for col in range(4):  # Only search in Name, Email, Team, Role
                item = self.members_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.members_table.setRowHidden(row, not match)

    def _create_audit_log_tab(self) -> QWidget:
        """Create audit log tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Activity Log")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        layout.addWidget(title)

        # Audit log table
        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(5)
        self.audit_table.setHorizontalHeaderLabels(
            ["User", "Action", "Resource Type", "Resource ID", "Timestamp"]
        )
        self._refresh_audit_log_table()
        layout.addWidget(self.audit_table)

        # Buttons
        button_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._refresh_audit_log_table)
        button_layout.addWidget(refresh_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def _refresh_teams_table(self):
        """Refresh teams table."""
        try:
            teams = TeamRepository.get_all_teams()
            self.teams_table.setRowCount(len(teams))

            for row, team in enumerate(teams):
                member_count = len(team.members) if team.members else 0

                self.teams_table.setItem(row, 0, QTableWidgetItem(team.name))
                self.teams_table.setItem(row, 1, QTableWidgetItem(team.team_id))
                self.teams_table.setItem(row, 2, QTableWidgetItem(team.division))
                self.teams_table.setItem(row, 3, QTableWidgetItem(str(member_count)))

                # Actions button
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                edit_btn = QPushButton("Edit")
                del_btn = QPushButton("Delete")
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(del_btn)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_widget.setLayout(actions_layout)
                self.teams_table.setCellWidget(row, 4, actions_widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load teams: {str(e)}")

    def _refresh_pending_users_table(self):
        """Refresh pending users table (now shows join requests)."""
        try:
            from app.database.repositories import TeamJoinRequestRepository, UserRepository, TeamRepository
            # Get all pending join requests
            pending_requests = TeamJoinRequestRepository.get_all_pending_requests() if hasattr(TeamJoinRequestRepository, 'get_all_pending_requests') else []
            # Get all unapproved users (admins & coaches for admin approval panel)
            unapproved_users = UserRepository.get_pending_users()
            # Combine: show coach join requests and unapproved users (admins & coaches)
            rows = []
            # Add coach join requests only
            for req in pending_requests:
                user = req.requester if hasattr(req, 'requester') and req.requester else UserRepository.get_user_by_id(req.requester_user_id)
                team = req.team if hasattr(req, 'team') and req.team else TeamRepository.get_team_by_id(req.team_id)
                # Only include coach requests here
                if not user or getattr(user, 'role', '').lower() != 'coach':
                    continue
                role_display = user.role.capitalize() if user and hasattr(user, 'role') else "N/A"
                team_name = team.name if team else "N/A"
                applied_date = getattr(req, 'created_at', None)
                applied_str = applied_date.strftime("%Y-%m-%d") if applied_date else "N/A"
                rows.append((user, role_display, team_name, applied_str, req.id, True))
            # Add unapproved users who are admins or coaches
            for user in unapproved_users:
                if getattr(user, 'role', '').lower() in ["coach", "admin"]:
                    team_name = user.team.name if user.team else "N/A"
                    applied_str = user.created_at.strftime("%Y-%m-%d") if hasattr(user, "created_at") and user.created_at else "N/A"
                    rows.append((user, user.role.capitalize(), team_name, applied_str, user.id, False))
            self.pending_table.setRowCount(len(rows))
            for row, (user, role_display, team_name, applied_str, obj_id, is_join_request) in enumerate(rows):
                self.pending_table.setItem(row, 0, QTableWidgetItem(user.name if user else "N/A"))
                self.pending_table.setItem(row, 1, QTableWidgetItem(user.email if user else "N/A"))
                self.pending_table.setItem(row, 2, QTableWidgetItem(role_display))
                self.pending_table.setItem(row, 3, QTableWidgetItem(team_name))
                self.pending_table.setItem(row, 4, QTableWidgetItem(applied_str))
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                approve_btn = QPushButton("Approve")
                reject_btn = QPushButton("Reject")
                if is_join_request:
                    approve_btn.clicked.connect(lambda checked, rid=obj_id: self._handle_approve_join_request(rid))
                    reject_btn.clicked.connect(lambda checked, rid=obj_id: self._handle_reject_join_request(rid))
                else:
                    approve_btn.clicked.connect(lambda checked, uid=obj_id: self._approve_user_by_id(uid))
                    reject_btn.clicked.connect(lambda checked, uid=obj_id: self._handle_reject_user(uid))
                actions_layout.addWidget(approve_btn)
                actions_layout.addWidget(reject_btn)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_widget.setLayout(actions_layout)
                self.pending_table.setCellWidget(row, 5, actions_widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load pending join requests: {str(e)}")

    def _handle_approve_join_request(self, request_id):
        from app.database.repositories import TeamJoinRequestRepository
        TeamJoinRequestRepository.approve_request(request_id)
        QMessageBox.information(self, "Success", "Join request approved.")
        self._refresh_pending_users_table()

    def _handle_reject_join_request(self, request_id):
        from app.database.repositories import TeamJoinRequestRepository
        TeamJoinRequestRepository.reject_request(request_id)
        QMessageBox.information(self, "Success", "Join request rejected.")
        self._refresh_pending_users_table()

    def _refresh_members_table(self):
        """Refresh members table with ALL users in the system."""
        try:
            from app.database.repositories import UserRepository
            # Get all users in the system (including admins, unapproved, etc.)
            all_users = UserRepository.get_all_users()

            self.members_table.setRowCount(len(all_users))

            for row, user in enumerate(all_users):
                team_name = user.team.name if user.team else "N/A"
                role_display = user.role if isinstance(user.role, str) else user.role.value
                approval_status = "Approved" if user.is_approved else "Pending"

                self.members_table.setItem(row, 0, QTableWidgetItem(user.name))
                self.members_table.setItem(row, 1, QTableWidgetItem(user.email))
                self.members_table.setItem(row, 2, QTableWidgetItem(team_name))
                self.members_table.setItem(row, 3, QTableWidgetItem(role_display.capitalize()))

                # Add approval status as additional info (or can be shown differently)
                approval_item = QTableWidgetItem(approval_status)
                self.members_table.setItem(row, 4, approval_item)

                # Actions - modify to accommodate approval status
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                
                if not user.is_approved:
                    approve_btn = QPushButton("Approve")
                    approve_btn.clicked.connect(lambda checked, uid=user.id: self._approve_user_by_id(uid))
                    actions_layout.addWidget(approve_btn)
                
                role_btn = QPushButton("Change Role")
                del_btn = QPushButton("Delete")
                role_btn.clicked.connect(lambda checked, uid=user.id: self._show_change_role_dialog(uid))
                del_btn.clicked.connect(lambda checked, uid=user.id: self._handle_remove_member_id(uid))
                actions_layout.addWidget(role_btn)
                actions_layout.addWidget(del_btn)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_widget.setLayout(actions_layout)
                self.members_table.setCellWidget(row, 5, actions_widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load members: {str(e)}")

    def _approve_user_by_id(self, user_id):
        """Approve a pending user by ID."""
        from app.database.repositories import UserRepository
        UserRepository.approve_user(user_id)
        QMessageBox.information(self, "Success", "User approved successfully.")
        self._refresh_members_table()

    def _refresh_audit_log_table(self):
        """Refresh audit log table."""
        try:
            logs = AuditLogRepository.get_audit_logs(limit=50)
            self.audit_table.setRowCount(len(logs))

            for row, log in enumerate(logs):
                user_name = log.user.name if log.user else "Unknown"

                self.audit_table.setItem(row, 0, QTableWidgetItem(user_name))
                self.audit_table.setItem(row, 1, QTableWidgetItem(log.action))
                self.audit_table.setItem(row, 2, QTableWidgetItem(log.resource_type))
                self.audit_table.setItem(row, 3, QTableWidgetItem(str(log.resource_id or "")))
                self.audit_table.setItem(row, 4, QTableWidgetItem(log.created_at.strftime("%Y-%m-%d %H:%M:%S")))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load audit logs: {str(e)}")

    def _show_create_team_dialog(self):
        """Show create team dialog."""
        dialog = CreateTeamDialog(self, self.admin_user["id"])
        if dialog.exec() == QDialog.Accepted:
            self._refresh_teams_table()

    def _show_edit_team_dialog(self):
        """Show edit team dialog."""
        current_row = self.teams_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a team to edit.")
            return

        team_id_str = self.teams_table.item(current_row, 1).text()
        team = TeamRepository.get_team_by_team_id(team_id_str)

        if team:
            dialog = EditTeamDialog(self, team)
            if dialog.exec() == QDialog.Accepted:
                self._refresh_teams_table()

    def _handle_delete_team(self):
        """Handle delete team."""
        current_row = self.teams_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a team to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this team and all its members?",
        )
        if reply == QMessageBox.Yes:
            try:
                team_id_str = self.teams_table.item(current_row, 1).text()
                team = TeamRepository.get_team_by_team_id(team_id_str)
                if team:
                    TeamRepository.delete_team(team.id)
                    QMessageBox.information(self, "Success", "Team deleted successfully.")
                    self._refresh_teams_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete team: {str(e)}")

    def _handle_approve_user(self, user_id: int):
        """Handle approve user."""
        try:
            UserRepository.approve_user(user_id)
            QMessageBox.information(self, "Success", "User approved successfully.")
            self._refresh_pending_users_table()
            AuditLogRepository.log_action(
                self.admin_user["id"], "approve", "user", user_id, "User approved"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to approve user: {str(e)}")

    def _handle_reject_user(self, user_id: int):
        """Handle reject user."""
        try:
            UserRepository.reject_user(user_id)
            QMessageBox.information(self, "Success", "User rejected and removed from system.")
            self._refresh_pending_users_table()
            AuditLogRepository.log_action(
                self.admin_user["id"], "reject", "user", user_id, "User rejected"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reject user: {str(e)}")

    def _show_change_role_dialog(self, user_id: int):
        """Show change role dialog."""
        dialog = ChangeRoleDialog(self, user_id)
        if dialog.exec() == QDialog.Accepted:
            self._refresh_members_table()
            AuditLogRepository.log_action(
                self.admin_user["id"], "change_role", "user", user_id, f"Role changed to {dialog.new_role}"
            )

    def _handle_remove_member(self):
        """Handle remove member."""
        current_row = self.members_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a member to remove.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            "Are you sure you want to remove this member from the team?",
        )
        if reply == QMessageBox.Yes:
            self._handle_remove_member_id(None)

    def _handle_remove_member_id(self, user_id: int):
        """Handle remove member by ID."""
        try:
            # Ask for confirmation, showing user details if available
            user = UserRepository.get_user_by_id(user_id)
            user_label = f"{user.name} <{user.email}>" if user else f"User ID {user_id}"
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to permanently delete {user_label}? This cannot be undone.",
            )
            if reply != QMessageBox.Yes:
                return
            UserRepository.delete_user(user_id)
            QMessageBox.information(self, "Success", "User account deleted.")
            self._refresh_members_table()
            AuditLogRepository.log_action(
                self.admin_user["id"], "remove", "user", user_id, "User removed from team"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove member: {str(e)}")

    def _handle_logout(self):
        """Handle logout."""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
        )
        if reply == QMessageBox.Yes:
            AuditLogRepository.log_action(self.admin_user["id"], "logout", "auth", description="Admin logged out")
            self.user_logged_out.emit()
            self.close()

    def _get_stylesheet(self) -> str:
        """Return the stylesheet."""
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QLabel {
            color: #333333;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QTableWidget {
            background-color: white;
            alternate-background-color: #f9f9f9;
        }
        QTabWidget::pane {
            border: 1px solid #cccccc;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            color: #333333;
            padding: 8px 20px;
        }
        QTabBar::tab:selected {
            background-color: #4CAF50;
            color: white;
        }
        """


class CreateTeamDialog(QDialog):
    """Dialog for creating a new team."""

    def __init__(self, parent=None, admin_id: int | None = None):
        super().__init__(parent)
        self.admin_id = admin_id
        self.setWindowTitle("Create Team")
        self.setGeometry(200, 200, 400, 250)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Team Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Team ID (format: NN-NNNN):"))
        self.team_id_input = QLineEdit()
        layout.addWidget(self.team_id_input)

        layout.addWidget(QLabel("Division:"))
        self.division_input = QLineEdit()
        layout.addWidget(self.division_input)

        button_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        cancel_btn = QPushButton("Cancel")
        create_btn.clicked.connect(self._handle_create)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _handle_create(self):
        """Handle create button."""
        name = self.name_input.text().strip()
        team_id = self.team_id_input.text().strip()
        division = self.division_input.text().strip()

        if not all([name, team_id, division]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            existing = TeamRepository.get_team_by_team_id(team_id)
            if existing:
                QMessageBox.warning(self, "Duplicate", "Team ID already exists.")
                return

            # Default creator to the admin opening this dialog
            creator_id = self.admin_id or 0
            TeamRepository.create_team(name, team_id, division, creator_id)
            QMessageBox.information(self, "Success", "Team created successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create team: {str(e)}")


class EditTeamDialog(QDialog):
    """Dialog for editing a team."""

    def __init__(self, parent=None, team=None):
        super().__init__(parent)
        self.team = team
        self.setWindowTitle("Edit Team")
        self.setGeometry(200, 200, 400, 250)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Team Name:"))
        self.name_input = QLineEdit()
        self.name_input.setText(self.team.name)
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Team ID (read-only):"))
        team_id_label = QLineEdit()
        team_id_label.setText(self.team.team_id)
        team_id_label.setReadOnly(True)
        layout.addWidget(team_id_label)

        layout.addWidget(QLabel("Division:"))
        self.division_input = QLineEdit()
        self.division_input.setText(self.team.division)
        layout.addWidget(self.division_input)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self._handle_save)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _handle_save(self):
        """Handle save button."""
        name = self.name_input.text().strip()
        division = self.division_input.text().strip()

        if not all([name, division]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            TeamRepository.update_team(self.team.id, name, division)
            QMessageBox.information(self, "Success", "Team updated successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update team: {str(e)}")


class ChangeRoleDialog(QDialog):
    """Dialog for changing user role."""

    def __init__(self, parent=None, user_id: int = None):
        super().__init__(parent)
        self.user_id = user_id
        self.new_role = None
        self.setWindowTitle("Change Role")
        self.setGeometry(200, 200, 300, 150)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select New Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Member", "Captain", "Coach"])
        layout.addWidget(self.role_combo)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self._handle_save)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _handle_save(self):
        """Handle save button."""
        try:
            new_role = self.role_combo.currentText().lower()
            UserRepository.update_user_role(self.user_id, new_role)
            self.new_role = new_role
            QMessageBox.information(self, "Success", "Role updated successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update role: {str(e)}")

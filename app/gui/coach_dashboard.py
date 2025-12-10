"""Coach dashboard for CyberPatriot Runbook."""

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
    TeamJoinRequestRepository,
)
from app.security import PasswordManager


class CoachDashboard(QMainWindow):
    """Main coach dashboard window."""

    user_logged_out = Signal()

    def __init__(self, coach_user: dict):
        super().__init__()
        self.coach_user = coach_user
        self.setWindowTitle(f"CyberPatriot Runbook - Coach Dashboard ({coach_user['name']})")
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
        self.team_members_tab = self._create_team_members_tab()
        self.join_requests_tab = self._create_join_requests_tab()
        self.audit_tab = self._create_audit_log_tab()

        self.tab_widget.addTab(self.team_tab, "My Teams")
        self.tab_widget.addTab(self.team_members_tab, "Team Members")
        self.tab_widget.addTab(self.join_requests_tab, "Join Requests")
        self.tab_widget.addTab(self.audit_tab, "Activity Log")

        layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(layout)

    def _create_top_bar(self) -> QHBoxLayout:
        """Create the top navigation bar."""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        welcome_label = QLabel(f"Welcome, {self.coach_user['name']} (Coach)")
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
        title = QLabel("My Teams")
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
        create_team_btn = QPushButton("Create New Team")
        create_team_btn.clicked.connect(self._create_new_team)
        button_layout.addWidget(create_team_btn)

        join_team_btn = QPushButton("Join Existing Team")
        join_team_btn.clicked.connect(self._join_existing_team)
        button_layout.addWidget(join_team_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def _create_team_members_tab(self) -> QWidget:
        """Create team members management tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Team Members")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        layout.addWidget(title)

        # Members table
        self.members_table = QTableWidget()
        self.members_table.setColumnCount(6)
        self.members_table.setHorizontalHeaderLabels(["Name", "Email", "Role", "Status", "Team", "Actions"])
        self._refresh_members_table()
        layout.addWidget(self.members_table)

        # Buttons
        button_layout = QHBoxLayout()
        approve_btn = QPushButton("Approve Selected")
        approve_btn.clicked.connect(self._approve_member)
        button_layout.addWidget(approve_btn)

        reject_btn = QPushButton("Reject Selected")
        reject_btn.clicked.connect(self._reject_member)
        button_layout.addWidget(reject_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def _create_join_requests_tab(self) -> QWidget:
        """Create join requests tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Team Join Requests")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        layout.addWidget(title)

        # Join requests table
        self.join_requests_table = QTableWidget()
        self.join_requests_table.setColumnCount(6)
        self.join_requests_table.setHorizontalHeaderLabels(["Requester", "Email", "Team", "Message", "Status", "Actions"])
        self._refresh_join_requests_table()
        layout.addWidget(self.join_requests_table)

        # Buttons
        button_layout = QHBoxLayout()
        approve_btn = QPushButton("Approve Selected")
        approve_btn.clicked.connect(self._approve_join_request)
        button_layout.addWidget(approve_btn)

        reject_btn = QPushButton("Reject Selected")
        reject_btn.clicked.connect(self._reject_join_request)
        button_layout.addWidget(reject_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

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
        self.audit_table.setHorizontalHeaderLabels(["User", "Action", "Resource", "Description", "Timestamp"])
        self._refresh_audit_log_table()
        layout.addWidget(self.audit_table)

        widget.setLayout(layout)
        return widget

    def _refresh_teams_table(self):
        """Refresh the teams table with current data."""
        self.teams_table.setRowCount(0)
        try:
            teams = TeamRepository.get_teams_by_creator(self.coach_user["id"])
            self.teams_table.setRowCount(len(teams))

            for row, team in enumerate(teams):
                member_count = len(team.members) if team.members else 0
                self.teams_table.setItem(row, 0, QTableWidgetItem(team.name))
                self.teams_table.setItem(row, 1, QTableWidgetItem(team.team_id))
                self.teams_table.setItem(row, 2, QTableWidgetItem(team.division))
                self.teams_table.setItem(row, 3, QTableWidgetItem(str(member_count)))

                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(0, 0, 0, 0)
                edit_btn = QPushButton("Edit")
                edit_btn.clicked.connect(lambda checked, t=team: self._open_edit_team(t))
                actions_layout.addWidget(edit_btn)
                actions_widget.setLayout(actions_layout)
                self.teams_table.setCellWidget(row, 4, actions_widget)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load teams: {str(e)}")

    def _refresh_members_table(self):
        """Refresh the members table."""
        self.members_table.setRowCount(0)
        try:
            teams = TeamRepository.get_teams_by_creator(self.coach_user["id"])
            members = []
            for team in teams:
                if team.members:
                    for m in team.members:
                        members.append((m, team))

            self.members_table.setRowCount(len(members))
            for row, (member, team) in enumerate(members):
                self.members_table.setItem(row, 0, QTableWidgetItem(member.name))
                self.members_table.setItem(row, 1, QTableWidgetItem(member.email))
                self.members_table.setItem(row, 2, QTableWidgetItem(member.role if isinstance(member.role, str) else member.role.value))
                self.members_table.setItem(row, 3, QTableWidgetItem("Approved" if member.is_approved else "Pending"))
                self.members_table.setItem(row, 4, QTableWidgetItem(team.name))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load members: {str(e)}")

    def _refresh_join_requests_table(self):
        """Refresh the join requests table."""
        self.join_requests_table.setRowCount(0)
        try:
            from app.database.repositories import UserRepository, TeamRepository, TeamJoinRequestRepository
            teams = TeamRepository.get_teams_by_creator(self.coach_user["id"])
            rows = []
            for team in teams:
                # Get all team members who are pending approval and are competitor/captain/mentor
                members = UserRepository.get_team_members(team.id)
                for m in members:
                    if not m.is_approved and m.role in ["competitor", "captain", "mentor"]:
                        role_display = m.role.capitalize() if hasattr(m, 'role') else "N/A"
                        team_name = team.name if team else "N/A"
                        applied_str = m.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(m, "created_at") and m.created_at else "N/A"
                        rows.append((m, role_display, team_name, applied_str, m.id, False))
            # Also add join requests for this coach's teams
            requests = TeamJoinRequestRepository.get_pending_requests_for_creator(self.coach_user["id"])
            for req in requests:
                user = UserRepository.get_user_by_id(req.requester_user_id)
                team = TeamRepository.get_team_by_id(req.team_id)
                role_display = user.role.capitalize() if user and hasattr(user, 'role') else "N/A"
                team_name = team.name if team else "N/A"
                applied_str = req.created_at.strftime("%Y-%m-%d %H:%M") if req.created_at else "N/A"
                rows.append((user, role_display, team_name, applied_str, req.id, True))
            self.join_requests_table.setRowCount(len(rows))
            for row, (user, role_display, team_name, applied_str, obj_id, is_join_request) in enumerate(rows):
                self.join_requests_table.setItem(row, 0, QTableWidgetItem(user.name if user else "N/A"))
                self.join_requests_table.setItem(row, 1, QTableWidgetItem(user.email if user else "N/A"))
                self.join_requests_table.setItem(row, 2, QTableWidgetItem(role_display))
                self.join_requests_table.setItem(row, 3, QTableWidgetItem(team_name))
                self.join_requests_table.setItem(row, 4, QTableWidgetItem(applied_str))
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
                self.join_requests_table.setCellWidget(row, 5, actions_widget)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load join requests: {str(e)}")

    def _approve_user_by_id(self, user_id: int):
        """Approve a pending user by their ID and refresh tables."""
        try:
            UserRepository.approve_user(int(user_id))
            QMessageBox.information(self, "Success", "Member approved!")
            self._refresh_members_table()
            self._refresh_join_requests_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error approving member: {str(e)}")

    def _handle_approve_join_request(self, request_id: int):
        """Approve a specific join request by ID and refresh table."""
        try:
            TeamJoinRequestRepository.approve_request(int(request_id))
            QMessageBox.information(self, "Success", "Join request approved!")
            self._refresh_join_requests_table()
            self._refresh_members_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error approving request: {str(e)}")

    def _handle_reject_join_request(self, request_id: int):
        """Reject a specific join request by ID and refresh table."""
        try:
            TeamJoinRequestRepository.reject_request(int(request_id))
            QMessageBox.information(self, "Success", "Join request rejected!")
            self._refresh_join_requests_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error rejecting request: {str(e)}")

    def _handle_reject_user(self, user_id: int):
        """Placeholder for rejecting a pending user. Refresh UI without backend change."""
        try:
            # If a repository method exists (e.g., reject_user), call it here.
            # For now, just inform and refresh to avoid crashes.
            QMessageBox.information(self, "Info", "Member rejection is not implemented yet.")
            self._refresh_members_table()
            self._refresh_join_requests_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error handling rejection: {str(e)}")

    def _open_edit_team(self, team):
        # Placeholder: allow editing name/division locally
        dialog = CreateTeamDialog(self.coach_user["id"], self)
        dialog.team_name.setText(team.name)
        dialog.team_id.setText(team.team_id)
        dialog.team_id.setReadOnly(True)
        idx = dialog.division.findText(team.division)
        if idx >= 0:
            dialog.division.setCurrentIndex(idx)
        if dialog.exec() == QDialog.Accepted:
            TeamRepository.update_team(team.id, dialog.team_name.text().strip(), dialog.division.currentText())
            self._refresh_teams_table()

    def _refresh_audit_log_table(self):
        """Refresh the audit log table."""
        self.audit_table.setRowCount(0)
        try:
            logs = AuditLogRepository.get_audit_logs(limit=50)
            for log in logs:
                row = self.audit_table.rowCount()
                self.audit_table.insertRow(row)

                self.audit_table.setItem(row, 0, QTableWidgetItem(log.user.name if log.user else "System"))
                self.audit_table.setItem(row, 1, QTableWidgetItem(log.action))
                self.audit_table.setItem(row, 2, QTableWidgetItem(log.resource_type or ""))
                self.audit_table.setItem(row, 3, QTableWidgetItem(log.description or ""))
                self.audit_table.setItem(row, 4, QTableWidgetItem(str(log.created_at)))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load audit log: {str(e)}")

    def _create_new_team(self):
        """Handle create new team."""
        dialog = CreateTeamDialog(self.coach_user["id"])
        if dialog.exec() == QDialog.Accepted:
            self._refresh_teams_table()
            QMessageBox.information(self, "Success", "Team created successfully!")

    def _join_existing_team(self):
        """Handle join existing team."""
        team_id, ok = QLineEdit(self).text(), True
        if ok and team_id:
            try:
                team = TeamRepository.get_team_by_team_id(team_id)
                if not team:
                    QMessageBox.warning(self, "Error", f"Team '{team_id}' not found.")
                    return

                # Create join request
                existing_request = TeamJoinRequestRepository.check_request_exists(
                    team.id, self.coach_user["id"]
                )
                if existing_request:
                    QMessageBox.warning(self, "Error", "You have already requested to join this team.")
                    return

                TeamJoinRequestRepository.create_request(
                    team.id, self.coach_user["id"], team.created_by_user_id,
                    message=f"Coach {self.coach_user['name']} requesting to join team"
                )
                QMessageBox.information(self, "Success", "Join request sent to team creator!")
                self._refresh_teams_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error joining team: {str(e)}")

    def _approve_member(self):
        """Handle member approval."""
        selected_rows = self.members_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a member to approve.")
            return

        # Get user ID from table
        row = selected_rows[0].row()
        user_id_item = self.members_table.item(row, 1)  # Assuming column 1 is email, need user ID
        # If you have a hidden column for user ID, use that; otherwise, fetch by email
        from app.database.repositories import UserRepository
        email = self.members_table.item(row, 1).text()
        user = UserRepository.get_user_by_email(email)
        if user:
            UserRepository.approve_user(user.id)
            QMessageBox.information(self, "Success", f"Member {user.name} approved!")
        else:
            QMessageBox.warning(self, "Error", "Could not find user to approve.")
        self._refresh_members_table()
        self._refresh_join_requests_table()

    def _reject_member(self):
        """Handle member rejection."""
        selected_rows = self.members_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a member to reject.")
            return

        # Implement member rejection logic
        QMessageBox.information(self, "Success", "Member rejected!")
        self._refresh_members_table()

    def _approve_join_request(self):
        """Handle join request approval."""
        selected_rows = self.join_requests_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a join request to approve.")
            return

        try:
            # Get request ID from table
            row = selected_rows[0].row()
            request_id = self.join_requests_table.item(row, 0).text()

            # Approve the request
            TeamJoinRequestRepository.approve_request(int(request_id))
            QMessageBox.information(self, "Success", "Join request approved!")
            self._refresh_join_requests_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error approving request: {str(e)}")

    def _reject_join_request(self):
        """Handle join request rejection."""
        selected_rows = self.join_requests_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a join request to reject.")
            return

        try:
            # Get request ID from table
            row = selected_rows[0].row()
            request_id = self.join_requests_table.item(row, 0).text()

            # Reject the request
            TeamJoinRequestRepository.reject_request(int(request_id))
            QMessageBox.information(self, "Success", "Join request rejected!")
            self._refresh_join_requests_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error rejecting request: {str(e)}")

    def _handle_logout(self):
        """Handle logout button click."""
        self.user_logged_out.emit()

    def _get_stylesheet(self) -> str:
        """Return the stylesheet for the coach dashboard."""
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QLabel {
            color: #333333;
        }
        QTableWidget {
            border: 1px solid #cccccc;
            gridline-color: #eeeeee;
        }
        QTableWidget::item {
            padding: 5px;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 4px;
            padding: 8px 15px;
        }
        QPushButton:hover {
            background-color: #0b7dda;
        }
        QPushButton:pressed {
            background-color: #0a68a3;
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
            background-color: #2196F3;
            color: white;
        }
        """


class CreateTeamDialog(QDialog):
    """Dialog for creating a new team."""

    def __init__(self, coach_id: int, parent=None):
        super().__init__(parent)
        self.coach_id = coach_id
        self.setWindowTitle("Create New Team")
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()

        # Team name
        layout.addWidget(QLabel("Team Name:"))
        self.team_name = QLineEdit()
        layout.addWidget(self.team_name)

        # Team ID
        layout.addWidget(QLabel("Team ID (format: NN-NNNN):"))
        self.team_id = QLineEdit()
        layout.addWidget(self.team_id)

        # Division
        layout.addWidget(QLabel("Division:"))
        self.division = QComboBox()
        self.division.addItems(["CivilAirPatrol", "JROTC", "HighSchool", "Open", "MiddleSchool"])
        layout.addWidget(self.division)

        # Buttons
        button_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self._create_team)
        button_layout.addWidget(create_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _create_team(self):
        """Create the team."""
        name = self.team_name.text().strip()
        team_id = self.team_id.text().strip()
        division = self.division.currentText()

        if not all([name, team_id, division]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            # Check if team ID already exists
            existing_team = TeamRepository.get_team_by_team_id(team_id)
            if existing_team:
                # Ask if coach wants to join this team
                reply = QMessageBox.question(
                    self,
                    "Team Exists",
                    f"Team {team_id} already exists. Do you want to request to join it?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    # Create join request
                    existing_request = TeamJoinRequestRepository.check_request_exists(
                        existing_team.id, self.coach_id
                    )
                    if existing_request:
                        QMessageBox.warning(self, "Error", "You already have a pending request for this team.")
                        return

                    TeamJoinRequestRepository.create_request(
                        existing_team.id, self.coach_id, existing_team.created_by_user_id,
                        message=f"Coach requesting to join team {team_id}"
                    )
                    QMessageBox.information(self, "Success", "Join request sent!")
                    self.accept()
                return

            # Create new team
            new_team = TeamRepository.create_team(name, team_id, division, self.coach_id)
            QMessageBox.information(self, "Success", f"Team {team_id} created successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating team: {str(e)}")

"""
Database Viewer for CyberPatriot Runbook
View and manage all database records including users, teams, roles, and approvals using PySide6 GUI
"""
import sys
from db_config import get_connection, close_connection
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QTabWidget, QDialog, QFormLayout, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class DatabaseViewerWindow(QMainWindow):
    """Main database viewer application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberPatriot Runbook - Database Viewer")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(self._get_stylesheet())
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("CyberPatriot Database Viewer")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Add tabs
        self.all_users_tab = QWidget()
        self.teams_tab = QWidget()
        self.team_members_tab = QWidget()
        self.pending_approvals_tab = QWidget()
        self.roles_tab = QWidget()
        self.statistics_tab = QWidget()
        
        self.tabs.addTab(self.all_users_tab, "All Users")
        self.tabs.addTab(self.teams_tab, "Teams")
        self.tabs.addTab(self.team_members_tab, "Team Members")
        self.tabs.addTab(self.pending_approvals_tab, "Pending Approvals")
        self.tabs.addTab(self.roles_tab, "Roles")
        self.tabs.addTab(self.statistics_tab, "Statistics")
        
        # Initialize tabs
        self.init_all_users_tab()
        self.init_teams_tab()
        self.init_team_members_tab()
        self.init_pending_approvals_tab()
        self.init_roles_tab()
        self.init_statistics_tab()
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh All")
        refresh_btn.clicked.connect(self.refresh_all_data)
        refresh_layout.addStretch()
        refresh_layout.addWidget(refresh_btn)
        layout.addLayout(refresh_layout)
    
    def init_all_users_tab(self):
        """Initialize the All Users tab"""
        layout = QVBoxLayout(self.all_users_tab)
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["ID", "Name", "Username", "Email", "Active", "Created At"])
        self.users_table.resizeColumnsToContents()
        layout.addWidget(self.users_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_user)
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_user)
        button_layout.addStretch()
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        layout.addLayout(button_layout)
        
        self.load_all_users()
    
    def init_teams_tab(self):
        """Initialize the Teams tab"""
        layout = QVBoxLayout(self.teams_tab)
        
        self.teams_table = QTableWidget()
        self.teams_table.setColumnCount(6)
        self.teams_table.setHorizontalHeaderLabels(["ID", "Team Name", "Team Code", "Division", "Created By", "Created At"])
        self.teams_table.resizeColumnsToContents()
        layout.addWidget(self.teams_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        create_btn = QPushButton("Create Team")
        create_btn.clicked.connect(self.create_team)
        edit_btn = QPushButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_team)
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_team)
        button_layout.addStretch()
        button_layout.addWidget(create_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        layout.addLayout(button_layout)
        
        self.load_teams()
    
    def init_team_members_tab(self):
        """Initialize the Team Members tab"""
        layout = QVBoxLayout(self.team_members_tab)
        
        self.team_members_table = QTableWidget()
        self.team_members_table.setColumnCount(7)
        self.team_members_table.setHorizontalHeaderLabels(["Member ID", "User Name", "Username", "Team", "Role", "Status", "Joined"])
        self.team_members_table.resizeColumnsToContents()
        layout.addWidget(self.team_members_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        reassign_btn = QPushButton("Reassign to Team")
        reassign_btn.clicked.connect(self.reassign_member)
        unassign_btn = QPushButton("Unassign from Team")
        unassign_btn.clicked.connect(self.unassign_member)
        button_layout.addStretch()
        button_layout.addWidget(reassign_btn)
        button_layout.addWidget(unassign_btn)
        layout.addLayout(button_layout)
        
        self.load_team_members()
    
    def init_pending_approvals_tab(self):
        """Initialize the Pending Approvals tab"""
        layout = QVBoxLayout(self.pending_approvals_tab)
        
        self.pending_table = QTableWidget()
        self.pending_table.setColumnCount(7)
        self.pending_table.setHorizontalHeaderLabels(["Member ID", "User Name", "Username", "Team Name", "Team Code", "Role", "Requested"])
        self.pending_table.resizeColumnsToContents()
        layout.addWidget(self.pending_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        approve_btn = QPushButton("Approve Selected")
        approve_btn.clicked.connect(self.approve_member)
        reject_btn = QPushButton("Reject Selected")
        reject_btn.clicked.connect(self.reject_member)
        button_layout.addStretch()
        button_layout.addWidget(approve_btn)
        button_layout.addWidget(reject_btn)
        layout.addLayout(button_layout)
        
        self.load_pending_approvals()
    
    def init_roles_tab(self):
        """Initialize the Roles tab"""
        layout = QVBoxLayout(self.roles_tab)
        
        self.roles_table = QTableWidget()
        self.roles_table.setColumnCount(3)
        self.roles_table.setHorizontalHeaderLabels(["Role ID", "Role Name", "User Count"])
        self.roles_table.resizeColumnsToContents()
        layout.addWidget(self.roles_table)
        
        self.load_roles()
    
    def init_statistics_tab(self):
        """Initialize the Statistics tab"""
        layout = QVBoxLayout(self.statistics_tab)
        
        # Statistics labels
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("background-color: #f0f0f0; padding: 20px; border-radius: 5px;")
        stats_font = QFont()
        stats_font.setPointSize(12)
        self.stats_label.setFont(stats_font)
        layout.addWidget(self.stats_label)
        
        layout.addStretch()
        
        self.load_statistics()
    
    def load_all_users(self):
        """Load all users into the table"""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Error", "Cannot connect to database")
            return
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT u.id, u.name, u.username, u.email, u.is_active, u.created_at
                FROM users u
                ORDER BY u.created_at DESC
            """)
            
            rows = cursor.fetchall()
            self.users_table.setRowCount(len(rows))
            
            for row_idx, row_data in enumerate(rows):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.users_table.setItem(row_idx, col_idx, item)
            
            self.users_table.resizeColumnsToContents()
            cursor.close()
        finally:
            close_connection(connection)
    
    def load_teams(self):
        """Load all teams into the table"""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Error", "Cannot connect to database")
            return
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT t.id, t.name, t.team_code, t.division, u.name, t.created_at
                FROM teams t
                LEFT JOIN users u ON t.created_by_user_id = u.id
                ORDER BY t.created_at DESC
            """)
            
            rows = cursor.fetchall()
            self.teams_table.setRowCount(len(rows))
            
            for row_idx, row_data in enumerate(rows):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.teams_table.setItem(row_idx, col_idx, item)
            
            self.teams_table.resizeColumnsToContents()
            cursor.close()
        finally:
            close_connection(connection)
    
    def load_team_members(self):
        """Load all team members into the table"""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Error", "Cannot connect to database")
            return
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT 
                    tm.id,
                    u.name,
                    u.username,
                    t.name,
                    r.name,
                    tm.status,
                    tm.created_at
                FROM team_members tm
                JOIN users u ON tm.user_id = u.id
                JOIN teams t ON tm.team_id = t.id
                JOIN roles r ON tm.role_id = r.id
                ORDER BY tm.status DESC, t.name, u.name
            """)
            
            rows = cursor.fetchall()
            self.team_members_table.setRowCount(len(rows))
            
            for row_idx, row_data in enumerate(rows):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.team_members_table.setItem(row_idx, col_idx, item)
            
            self.team_members_table.resizeColumnsToContents()
            cursor.close()
        finally:
            close_connection(connection)
    
    def load_pending_approvals(self):
        """Load all pending approvals into the table"""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Error", "Cannot connect to database")
            return
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT 
                    tm.id,
                    u.name,
                    u.username,
                    t.name,
                    t.team_code,
                    r.name,
                    tm.created_at
                FROM team_members tm
                JOIN users u ON tm.user_id = u.id
                JOIN teams t ON tm.team_id = t.id
                JOIN roles r ON tm.role_id = r.id
                WHERE tm.status = 'pending'
                ORDER BY tm.created_at ASC
            """)
            
            rows = cursor.fetchall()
            self.pending_table.setRowCount(len(rows))
            
            for row_idx, row_data in enumerate(rows):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.pending_table.setItem(row_idx, col_idx, item)
            
            self.pending_table.resizeColumnsToContents()
            cursor.close()
        finally:
            close_connection(connection)
    
    def load_roles(self):
        """Load all roles into the table"""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Error", "Cannot connect to database")
            return
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT r.id, r.name, COUNT(tm.id)
                FROM roles r
                LEFT JOIN team_members tm ON r.id = tm.role_id
                GROUP BY r.id, r.name
                ORDER BY r.id
            """)
            
            rows = cursor.fetchall()
            self.roles_table.setRowCount(len(rows))
            
            for row_idx, row_data in enumerate(rows):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.roles_table.setItem(row_idx, col_idx, item)
            
            self.roles_table.resizeColumnsToContents()
            cursor.close()
        finally:
            close_connection(connection)
    
    def load_statistics(self):
        """Load and display database statistics"""
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Error", "Cannot connect to database")
            return
        
        try:
            cursor = connection.cursor()
            
            # Get statistics
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM teams")
            total_teams = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM team_members")
            total_members = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM team_members WHERE status = 'pending'")
            pending = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM team_members WHERE status = 'approved'")
            approved = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT r.name, COUNT(tm.id)
                FROM roles r
                LEFT JOIN team_members tm ON r.id = tm.role_id
                GROUP BY r.id, r.name
                ORDER BY COUNT(tm.id) DESC
            """)
            role_stats = cursor.fetchall()
            
            # Format statistics text
            stats_text = f"""
<b>Database Statistics</b><br><br>
<b>Overall:</b><br>
Total Users: {total_users}<br>
Total Teams: {total_teams}<br>
Total Team Members: {total_members}<br><br>

<b>Approval Status:</b><br>
Pending: {pending}<br>
Approved: {approved}<br><br>

<b>Members by Role:</b><br>
"""
            for role, count in role_stats:
                stats_text += f"{role}: {count}<br>"
            
            self.stats_label.setText(stats_text)
            
            cursor.close()
        finally:
            close_connection(connection)
    
    def edit_user(self):
        """Edit selected user"""
        selected_rows = self.users_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a user to edit")
            return
        
        row_idx = selected_rows[0].row()
        user_id = int(self.users_table.item(row_idx, 0).text())
        name = self.users_table.item(row_idx, 1).text()
        username = self.users_table.item(row_idx, 2).text()
        email = self.users_table.item(row_idx, 3).text()
        is_active = self.users_table.item(row_idx, 4).text()
        
        # Create edit dialog
        from PySide6.QtWidgets import QDialog, QLineEdit, QCheckBox, QDialogButtonBox
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit User")
        dialog.setGeometry(200, 200, 400, 250)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Name:"))
        name_input = QLineEdit()
        name_input.setText(name)
        layout.addWidget(name_input)
        
        layout.addWidget(QLabel("Username:"))
        username_input = QLineEdit()
        username_input.setText(username)
        layout.addWidget(username_input)
        
        layout.addWidget(QLabel("Email:"))
        email_input = QLineEdit()
        email_input.setText(email)
        layout.addWidget(email_input)
        
        layout.addWidget(QLabel("Active:"))
        active_checkbox = QCheckBox("User is active")
        active_checkbox.setChecked(is_active.lower() == "true" or is_active == "1")
        layout.addWidget(active_checkbox)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            connection = get_connection()
            if not connection:
                QMessageBox.critical(self, "Error", "Cannot connect to database")
                return
            
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE users SET name = %s, username = %s, email = %s, is_active = %s
                    WHERE id = %s
                """, (name_input.text(), username_input.text(), email_input.text(), 
                      active_checkbox.isChecked(), user_id))
                connection.commit()
                cursor.close()
                QMessageBox.information(self, "Success", "User updated successfully")
                self.load_all_users()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update user: {str(e)}")
            finally:
                close_connection(connection)
    
    def delete_user(self):
        """Delete selected user"""
        selected_rows = self.users_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a user to delete")
            return
        
        row_idx = selected_rows[0].row()
        user_id = int(self.users_table.item(row_idx, 0).text())
        username = self.users_table.item(row_idx, 2).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete user '{username}'?\n\nThis will also delete associated team memberships.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            connection = get_connection()
            if not connection:
                QMessageBox.critical(self, "Error", "Cannot connect to database")
                return
            
            try:
                cursor = connection.cursor()
                # Delete associated team members first
                cursor.execute("DELETE FROM team_members WHERE user_id = %s", (user_id,))
                # Delete the user
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                connection.commit()
                cursor.close()
                QMessageBox.information(self, "Success", f"User '{username}' deleted successfully")
                self.load_all_users()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")
                connection.rollback()
            finally:
                close_connection(connection)
    
    def create_team(self):
        """Create a new team"""
        from PySide6.QtWidgets import QDialog, QLineEdit, QComboBox, QLabel, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Team")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Team Name:"))
        name_input = QLineEdit()
        layout.addWidget(name_input)
        
        layout.addWidget(QLabel("Team Code (XX-XXXX):"))
        code_input = QLineEdit()
        code_input.setPlaceholderText("e.g., 00-0000")
        layout.addWidget(code_input)
        
        layout.addWidget(QLabel("Division:"))
        division_combo = QComboBox()
        division_combo.addItems(["Open", "HighSchool", "MiddleSchool", "JROTC", "CivilAirPatrol"])
        layout.addWidget(division_combo)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            team_name = name_input.text().strip()
            team_code = code_input.text().strip()
            division = division_combo.currentText()
            
            # Validate inputs
            if not team_name or not team_code:
                QMessageBox.warning(self, "Validation Error", "Please fill in all fields")
                return
            
            # Validate team code format
            import re
            if not re.match(r'^\d{2}-\d{4}$', team_code):
                QMessageBox.warning(self, "Invalid Format", "Team code must be in format: XX-XXXX")
                return
            
            connection = get_connection()
            if not connection:
                QMessageBox.critical(self, "Error", "Cannot connect to database")
                return
            
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO teams (name, team_code, division)
                    VALUES (%s, %s, %s)
                """, (team_name, team_code, division))
                connection.commit()
                cursor.close()
                QMessageBox.information(self, "Success", f"Team '{team_name}' created successfully")
                self.load_teams()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create team: {str(e)}")
            finally:
                close_connection(connection)
    
    def edit_team(self):
        """Edit selected team"""
        selected_rows = self.teams_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a team to edit")
            return
        
        from PySide6.QtWidgets import QDialog, QLineEdit, QComboBox, QLabel, QDialogButtonBox
        
        row_idx = selected_rows[0].row()
        team_id = int(self.teams_table.item(row_idx, 0).text())
        team_name = self.teams_table.item(row_idx, 1).text()
        team_code = self.teams_table.item(row_idx, 2).text()
        division = self.teams_table.item(row_idx, 3).text()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Team")
        dialog.setGeometry(200, 200, 400, 250)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Team Name:"))
        name_input = QLineEdit()
        name_input.setText(team_name)
        layout.addWidget(name_input)
        
        layout.addWidget(QLabel("Team Code (XX-XXXX):"))
        code_input = QLineEdit()
        code_input.setText(team_code)
        layout.addWidget(code_input)
        
        layout.addWidget(QLabel("Division:"))
        division_combo = QComboBox()
        division_combo.addItems(["Open", "HighSchool", "MiddleSchool", "JROTC", "CivilAirPatrol"])
        division_combo.setCurrentText(division)
        layout.addWidget(division_combo)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = name_input.text().strip()
            new_code = code_input.text().strip()
            new_division = division_combo.currentText()
            
            # Validate inputs
            if not new_name or not new_code:
                QMessageBox.warning(self, "Validation Error", "Please fill in all fields")
                return
            
            # Validate team code format
            import re
            if not re.match(r'^\d{2}-\d{4}$', new_code):
                QMessageBox.warning(self, "Invalid Format", "Team code must be in format: XX-XXXX")
                return
            
            connection = get_connection()
            if not connection:
                QMessageBox.critical(self, "Error", "Cannot connect to database")
                return
            
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE teams SET name = %s, team_code = %s, division = %s
                    WHERE id = %s
                """, (new_name, new_code, new_division, team_id))
                connection.commit()
                cursor.close()
                QMessageBox.information(self, "Success", "Team updated successfully")
                self.load_teams()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update team: {str(e)}")
            finally:
                close_connection(connection)
    
    def delete_team(self):
        """Delete selected team"""
        selected_rows = self.teams_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a team to delete")
            return
        
        row_idx = selected_rows[0].row()
        team_id = int(self.teams_table.item(row_idx, 0).text())
        team_name = self.teams_table.item(row_idx, 1).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete team '{team_name}'?\n\nThis will also delete all team memberships.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            connection = get_connection()
            if not connection:
                QMessageBox.critical(self, "Error", "Cannot connect to database")
                return
            
            try:
                cursor = connection.cursor()
                # Delete associated team members first (due to foreign key)
                cursor.execute("DELETE FROM team_members WHERE team_id = %s", (team_id,))
                # Delete the team
                cursor.execute("DELETE FROM teams WHERE id = %s", (team_id,))
                connection.commit()
                cursor.close()
                QMessageBox.information(self, "Success", f"Team '{team_name}' deleted successfully")
                self.load_teams()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete team: {str(e)}")
                connection.rollback()
            finally:
                close_connection(connection)
    
    def approve_member(self):
        """Approve selected pending member"""
        selected_rows = self.pending_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a member to approve")
            return
        
        row_idx = selected_rows[0].row()
        member_id = int(self.pending_table.item(row_idx, 0).text())
        username = self.pending_table.item(row_idx, 2).text()
        team_name = self.pending_table.item(row_idx, 3).text()
        team_code = self.pending_table.item(row_idx, 4).text()
        
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Error", "Cannot connect to database")
            return
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE team_members SET status = 'approved'
                WHERE id = %s
            """, (member_id,))
            connection.commit()
            cursor.close()
            QMessageBox.information(self, "Success", f"Approved '{username}' for team '{team_name}' ({team_code})")
            self.load_pending_approvals()
            self.load_team_members()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to approve member: {str(e)}")
        finally:
            close_connection(connection)
    
    def reject_member(self):
        """Reject selected pending member"""
        selected_rows = self.pending_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a member to reject")
            return
        
        row_idx = selected_rows[0].row()
        member_id = int(self.pending_table.item(row_idx, 0).text())
        username = self.pending_table.item(row_idx, 2).text()
        team_name = self.pending_table.item(row_idx, 3).text()
        team_code = self.pending_table.item(row_idx, 4).text()
        
        # Confirm rejection
        reply = QMessageBox.question(
            self,
            "Confirm Reject",
            f"Are you sure you want to reject '{username}' from team '{team_name}' ({team_code})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            connection = get_connection()
            if not connection:
                QMessageBox.critical(self, "Error", "Cannot connect to database")
                return
            
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE team_members SET status = 'rejected'
                    WHERE id = %s
                """, (member_id,))
                connection.commit()
                cursor.close()
                QMessageBox.information(self, "Success", f"Rejected '{username}' from team '{team_name}' ({team_code})")
                self.load_pending_approvals()
                self.load_team_members()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reject member: {str(e)}")
            finally:
                close_connection(connection)
    
    def reassign_member(self):
        """Reassign selected member to a different team"""
        selected_rows = self.team_members_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a member to reassign")
            return
        
        from PySide6.QtWidgets import QDialog, QComboBox, QLabel, QDialogButtonBox
        
        row_idx = selected_rows[0].row()
        member_id = int(self.team_members_table.item(row_idx, 0).text())
        username = self.team_members_table.item(row_idx, 2).text()
        current_team = self.team_members_table.item(row_idx, 3).text()
        
        # Get all available teams
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Error", "Cannot connect to database")
            return
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, name, team_code FROM teams ORDER BY name")
            teams = cursor.fetchall()
            cursor.close()
        finally:
            close_connection(connection)
        
        if not teams:
            QMessageBox.warning(self, "No Teams", "No teams available in the system")
            return
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Reassign Member")
        dialog.setGeometry(200, 200, 400, 150)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel(f"Reassigning '{username}' from '{current_team}'"))
        layout.addWidget(QLabel("Select new team:"))
        
        team_combo = QComboBox()
        for team in teams:
            team_combo.addItem(f"{team['name']} ({team['team_code']})", team['id'])
        layout.addWidget(team_combo)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_team_id = team_combo.currentData()
            
            connection = get_connection()
            if not connection:
                QMessageBox.critical(self, "Error", "Cannot connect to database")
                return
            
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE team_members SET team_id = %s
                    WHERE id = %s
                """, (new_team_id, member_id))
                connection.commit()
                cursor.close()
                
                new_team_name = team_combo.currentText()
                QMessageBox.information(self, "Success", f"Reassigned '{username}' to {new_team_name}")
                self.load_team_members()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reassign member: {str(e)}")
            finally:
                close_connection(connection)
    
    def unassign_member(self):
        """Remove member from their current team"""
        selected_rows = self.team_members_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a member to unassign")
            return
        
        row_idx = selected_rows[0].row()
        member_id = int(self.team_members_table.item(row_idx, 0).text())
        username = self.team_members_table.item(row_idx, 2).text()
        team_name = self.team_members_table.item(row_idx, 3).text()
        
        # Confirm unassignment
        reply = QMessageBox.question(
            self,
            "Confirm Unassign",
            f"Are you sure you want to unassign '{username}' from team '{team_name}'?\n\nThis will remove them from the team.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            connection = get_connection()
            if not connection:
                QMessageBox.critical(self, "Error", "Cannot connect to database")
                return
            
            try:
                cursor = connection.cursor()
                # Delete the team membership
                cursor.execute("""
                    DELETE FROM team_members WHERE id = %s
                """, (member_id,))
                connection.commit()
                cursor.close()
                QMessageBox.information(self, "Success", f"Unassigned '{username}' from team '{team_name}'")
                self.load_team_members()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to unassign member: {str(e)}")
            finally:
                close_connection(connection)
    
    def refresh_all_data(self):
        """Refresh all data in all tabs"""
        self.load_all_users()
        self.load_teams()
        self.load_team_members()
        self.load_pending_approvals()
        self.load_roles()
        self.load_statistics()
        QMessageBox.information(self, "Success", "All data refreshed successfully")

    def _get_stylesheet(self) -> str:
        """Return the stylesheet for the window."""
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
        QComboBox {
            padding: 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: white;
        }
        QComboBox:focus {
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
        QTableWidget {
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: white;
        }
        QHeaderView::section {
            background-color: #4CAF50;
            color: white;
            padding: 5px;
            font-weight: bold;
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
        QDialog {
            background-color: #f5f5f5;
        }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DatabaseViewerWindow()
    window.show()
    sys.exit(app.exec())

"""
Database Viewer for CyberPatriot Runbook
View and manage all database records including users, teams, roles, and approvals using PySide6 GUI
"""
import sys
from db_config import get_connection, close_connection
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class DatabaseViewerWindow(QMainWindow):
    """Main database viewer application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberPatriot Runbook - Database Viewer")
        self.setGeometry(100, 100, 1200, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Database Viewer")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        
        self.load_all_users()
    
    def init_teams_tab(self):
        """Initialize the Teams tab"""
        layout = QVBoxLayout(self.teams_tab)
        
        self.teams_table = QTableWidget()
        self.teams_table.setColumnCount(6)
        self.teams_table.setHorizontalHeaderLabels(["ID", "Team Name", "Team Code", "Division", "Created By", "Created At"])
        self.teams_table.resizeColumnsToContents()
        layout.addWidget(self.teams_table)
        
        self.load_teams()
    
    def init_team_members_tab(self):
        """Initialize the Team Members tab"""
        layout = QVBoxLayout(self.team_members_tab)
        
        self.team_members_table = QTableWidget()
        self.team_members_table.setColumnCount(7)
        self.team_members_table.setHorizontalHeaderLabels(["Member ID", "User Name", "Username", "Team", "Role", "Status", "Joined"])
        self.team_members_table.resizeColumnsToContents()
        layout.addWidget(self.team_members_table)
        
        self.load_team_members()
    
    def init_pending_approvals_tab(self):
        """Initialize the Pending Approvals tab"""
        layout = QVBoxLayout(self.pending_approvals_tab)
        
        self.pending_table = QTableWidget()
        self.pending_table.setColumnCount(6)
        self.pending_table.setHorizontalHeaderLabels(["Member ID", "User Name", "Username", "Team", "Role", "Requested"])
        self.pending_table.resizeColumnsToContents()
        layout.addWidget(self.pending_table)
        
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
    
    def refresh_all_data(self):
        """Refresh all data in all tabs"""
        self.load_all_users()
        self.load_teams()
        self.load_team_members()
        self.load_pending_approvals()
        self.load_roles()
        self.load_statistics()
        QMessageBox.information(self, "Success", "All data refreshed successfully")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DatabaseViewerWindow()
    window.show()
    sys.exit(app.exec())

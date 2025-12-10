"""Script for team members to upload and view shared README files."""

import sys
import json
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QComboBox,
    QFileDialog,
    QDialog,
    QFormLayout,
    QLineEdit,
    QScrollArea,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor
from db_config import get_connection, close_connection


class ReadmeViewerWindow(QMainWindow):
    """Main window for viewing and uploading README files."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberPatriot Team README Viewer")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(self._get_stylesheet())
        self.teams = self._load_teams()
        self.current_user_id = None
        self.current_username = None
        self.current_team_id = None
        self._init_ui()

    def _load_teams(self):
        """Load teams from the database."""
        from db_config import get_connection, close_connection
        
        teams = {}
        connection = get_connection()
        if not connection:
            return teams
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, name FROM teams ORDER BY name")
            results = cursor.fetchall()
            for row in results:
                teams[row['name']] = row['id']
            cursor.close()
        except Exception:
            pass
        finally:
            close_connection(connection)
        
        return teams

    def _get_team_members(self, team_id):
        """Get all members of a specific team."""
        from db_config import get_connection, close_connection
        
        members = {}
        connection = get_connection()
        if not connection:
            return members
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT u.id, u.username FROM users u "
                "JOIN team_members tm ON u.id = tm.user_id "
                "WHERE tm.team_id = %s AND tm.status = 'approved' "
                "ORDER BY u.username",
                (team_id,)
            )
            results = cursor.fetchall()
            for row in results:
                members[row['username']] = row['id']
            cursor.close()
        except Exception:
            pass
        finally:
            close_connection(connection)
        
        return members

    def _init_ui(self):
        """Initialize the main UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Team README Viewer")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(title)

        # Team selection
        team_layout = QHBoxLayout()
        team_label = QLabel("Select Team:")
        team_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.team_combo = QComboBox()
        self.team_combo.currentTextChanged.connect(self._on_team_changed)
        team_layout.addWidget(team_label)
        team_layout.addWidget(self.team_combo)
        team_layout.addStretch()
        main_layout.addLayout(team_layout)

        # Two-panel layout
        content_layout = QHBoxLayout()

        # Left panel: Members list
        left_panel = QVBoxLayout()
        members_label = QLabel("Team Members:")
        members_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_panel.addWidget(members_label)

        self.members_list = QListWidget()
        self.members_list.itemClicked.connect(self._on_member_clicked)
        left_panel.addWidget(self.members_list)

        # Right panel: README content
        right_panel = QVBoxLayout()
        readme_title_label = QLabel("Member README:")
        readme_title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_panel.addWidget(readme_title_label)

        self.member_name_label = QLabel("")
        self.member_name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        right_panel.addWidget(self.member_name_label)

        self.readme_content = QTextEdit()
        self.readme_content.setReadOnly(True)
        right_panel.addWidget(self.readme_content)

        # Action buttons
        button_layout = QHBoxLayout()
        upload_btn = QPushButton("Upload My README")
        upload_btn.clicked.connect(self._upload_readme)
        download_btn = QPushButton("Download Selected README")
        download_btn.clicked.connect(self._download_readme)
        button_layout.addWidget(upload_btn)
        button_layout.addWidget(download_btn)
        button_layout.addStretch()
        right_panel.addLayout(button_layout)

        # Add panels to content layout
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(250)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        content_layout.addWidget(left_widget)
        content_layout.addWidget(right_widget)

        main_layout.addLayout(content_layout)

        # Bottom buttons
        bottom_button_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_members)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        bottom_button_layout.addWidget(refresh_btn)
        bottom_button_layout.addStretch()
        bottom_button_layout.addWidget(close_btn)
        main_layout.addLayout(bottom_button_layout)

        central_widget.setLayout(main_layout)
        self._load_teams_combo()

    def _load_teams_combo(self):
        """Load teams into the combo box."""
        self.team_combo.clear()
        if self.teams:
            self.team_combo.addItems(sorted(self.teams.keys()))
        else:
            self.team_combo.addItem("No teams available")

    def _on_team_changed(self, team_name):
        """Handle team selection change."""
        if not team_name or team_name == "No teams available":
            self.members_list.clear()
            self.readme_content.setPlainText("")
            self.current_team_id = None
            return
        
        self.current_team_id = self.teams.get(team_name)
        self._refresh_members()

    def _refresh_members(self):
        """Load and display team members."""
        selected_team = self.team_combo.currentText()
        if not selected_team or selected_team == "No teams available":
            self.members_list.clear()
            return

        team_id = self.teams.get(selected_team)
        if not team_id:
            return

        members = self._get_team_members(team_id)
        self.members_list.clear()

        for username, user_id in sorted(members.items()):
            list_item = QListWidgetItem(username)
            list_item.setData(Qt.ItemDataRole.UserRole, user_id)
            self.members_list.addItem(list_item)

    def _on_member_clicked(self, item):
        """Handle member selection."""
        username = item.text()
        self.member_name_label.setText(f"README - {username}")
        self._load_readme(username)

    def _load_readme(self, username):
        """Load README content for a member from database."""
        if not self.current_team_id:
            self.readme_content.setPlainText("No team selected.")
            return

        connection = get_connection()
        if not connection:
            self.readme_content.setPlainText("Database connection error.")
            return

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT content FROM readmes WHERE team_id = %s AND user_id = "
                "(SELECT id FROM users WHERE username = %s)",
                (self.current_team_id, username)
            )
            result = cursor.fetchone()
            cursor.close()

            if result:
                self.readme_content.setPlainText(result['content'])
            else:
                self.readme_content.setPlainText("No README file uploaded yet.")
        except Exception as e:
            self.readme_content.setPlainText(f"Error reading file: {str(e)}")
        finally:
            close_connection(connection)

    def _upload_readme(self):
        """Upload a README file to database."""
        team_name = self.team_combo.currentText()
        if not team_name or team_name == "No teams available":
            QMessageBox.warning(self, "No Team", "Please select a team first.")
            return

        # Get username and os_type from user input
        dialog = QDialog(self)
        dialog.setWindowTitle("Upload README")
        dialog.setGeometry(150, 150, 400, 200)
        dialog.setStyleSheet(self._get_stylesheet())
        
        layout = QFormLayout()
        username_label = QLabel("Your Username:")
        username_input = QLineEdit()
        username_input.setPlaceholderText("Enter your username")
        layout.addRow(username_label, username_input)

        os_label = QLabel("OS Type:")
        os_combo = QComboBox()
        os_combo.addItems(["Windows", "Linux", "Cisco", "Other"])
        layout.addRow(os_label, os_combo)

        button_box = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        button_box.addWidget(ok_btn)
        button_box.addWidget(cancel_btn)
        layout.addRow(button_box)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            username = username_input.text().strip()
            os_type = os_combo.currentText()
            if not username:
                QMessageBox.warning(self, "Invalid Input", "Please enter your username.")
                return

            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select README File",
                "",
                "Text Files (*.txt);;All Files (*)"
            )

            if file_path:
                try:
                    with open(file_path, "r") as f:
                        content = f.read()
                    
                    connection = get_connection()
                    if not connection:
                        QMessageBox.critical(self, "Error", "Could not connect to database.")
                        return

                    cursor = connection.cursor()
                    
                    # Get user_id from username
                    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                    user_result = cursor.fetchone()
                    if not user_result:
                        QMessageBox.warning(self, "User Not Found", f"User '{username}' not found.")
                        cursor.close()
                        close_connection(connection)
                        return
                    
                    user_id = user_result[0]
                    team_id = self.current_team_id

                    # Update or insert README
                    cursor.execute(
                        "INSERT INTO readmes (team_id, user_id, title, os_type, content) "
                        "VALUES (%s, %s, %s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE content = VALUES(content), os_type = VALUES(os_type), updated_at = CURRENT_TIMESTAMP",
                        (team_id, user_id, f"{username}'s README", os_type, content)
                    )
                    
                    connection.commit()
                    cursor.close()
                    close_connection(connection)

                    QMessageBox.information(self, "Success", "README uploaded successfully!")
                    self._refresh_members()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to upload README: {str(e)}")

    def _download_readme(self):
        """Download the selected README file."""
        current_item = self.members_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a member first.")
            return

        username = current_item.text()
        
        connection = get_connection()
        if not connection:
            QMessageBox.critical(self, "Error", "Could not connect to database.")
            return

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT content FROM readmes WHERE team_id = %s AND user_id = "
                "(SELECT id FROM users WHERE username = %s)",
                (self.current_team_id, username)
            )
            result = cursor.fetchone()
            cursor.close()

            if not result:
                QMessageBox.warning(self, "File Not Found", f"No README file found for {username}.")
                close_connection(connection)
                return

            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save README File",
                f"{username}_readme.txt",
                "Text Files (*.txt);;All Files (*)"
            )

            if save_path:
                with open(save_path, "w") as f:
                    f.write(result['content'])
                QMessageBox.information(self, "Success", "README downloaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download README: {str(e)}")
        finally:
            close_connection(connection)

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
        QListWidget {
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: white;
        }
        QListWidget::item:hover {
            background-color: #e8f5e9;
        }
        QListWidget::item:selected {
            background-color: #4CAF50;
            color: white;
        }
        QTextEdit {
            background-color: white;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 8px;
        }
        QDialog {
            background-color: #f5f5f5;
        }
        QFormLayout {
            color: #333333;
        }
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReadmeViewerWindow()
    window.show()
    sys.exit(app.exec())

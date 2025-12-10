from PySide6.QtWidgets import QVBoxLayout as QtQVBoxLayout
"""Member dashboard for CyberPatriot Runbook."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QTextEdit,
    QComboBox,
    QDialog,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QCheckBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.database.repositories import (
    ChecklistRepository,
    ReadMeRepository,
    NoteRepository,
    AuditLogRepository,
    UserRepository,
    TeamRepository,
)
from app.security import EncryptionManager


class MemberDashboard(QMainWindow):
    """Member dashboard window."""

    user_logged_out = Signal()

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"CyberPatriot Runbook - {user['name']}")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(self._get_stylesheet())

        # Create central widget with tabs
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QtQVBoxLayout()

        # Top bar with logout button and status
        top_bar = self._create_top_bar()
        layout.addLayout(top_bar)

        # Status message for team membership
        self.status_label = QLabel()
        self._update_team_status()
        layout.addWidget(self.status_label)

        # Tab widget for different sections

        self.tab_widget = QTabWidget()
        self.checklist_tab = self._create_checklist_tab()
        self.readme_tab = self._create_readme_tab()
        self.notes_tab = self._create_notes_tab()
        self.members_tab = self._create_team_members_tab()
        self.join_requests_tab = self._create_join_requests_tab()

        # All members see checklists, READMEs, and notes
        self.tab_widget.addTab(self.checklist_tab, "Checklists")
        self.tab_widget.addTab(self.readme_tab, "READMEs")
        self.tab_widget.addTab(self.notes_tab, "Notes")

        # Captains see team members and join requests
        if self.user["role"].lower() == "captain":
            self.tab_widget.addTab(self.members_tab, "Team Members")
            self.tab_widget.addTab(self.join_requests_tab, "Join Requests")
        # Regular members only see join requests (to request to join a team)
        elif self.user["role"].lower() == "member":
            self.tab_widget.addTab(self.join_requests_tab, "Join Requests")

        self.central_widget.setLayout(layout)
    def _create_team_members_tab(self) -> QWidget:
        widget = QWidget()
        layout = QtQVBoxLayout()
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Name", "Email", "Role"])
        members = []
        try:
            from app.database.repositories import UserRepository, TeamRepository
            # Fetch current user and their team with members via repositories
            user = UserRepository.get_user_by_id(self.user["id"])  
            team = TeamRepository.get_team_by_id(user.team_id) if user and user.team_id else None
            if team and team.members:
                members = team.members
        except Exception as e:
            # Show error in a copyable text box
            from PySide6.QtWidgets import QTextEdit, QDialog, QVBoxLayout, QPushButton
            error_dialog = QDialog(self)
            error_dialog.setWindowTitle("Error")
            error_layout = QVBoxLayout()
            error_box = QTextEdit()
            error_box.setReadOnly(True)
            error_box.setText(str(e))
            error_layout.addWidget(error_box)
            ok_btn = QPushButton("OK")
            ok_btn.clicked.connect(error_dialog.accept)
            error_layout.addWidget(ok_btn)
            error_dialog.setLayout(error_layout)
            error_dialog.exec()
        table.setRowCount(len(members))
        for row, member in enumerate(members):
            table.setItem(row, 0, QTableWidgetItem(member.name))
            table.setItem(row, 1, QTableWidgetItem(member.email))
            table.setItem(row, 2, QTableWidgetItem(str(member.role)))
        layout.addWidget(table)
        widget.setLayout(layout)
        return widget

    def _create_join_requests_tab(self) -> QWidget:
        widget = QWidget()
        layout = QtQVBoxLayout()
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Name", "Email", "Role", "Approve", "Reject"])
        requests = []
        try:
            user = UserRepository.get_user_by_id(self.user["id"])
            if user and user.team_id:
                from app.database.repositories import TeamJoinRequestRepository, UserRepository
                requests = TeamJoinRequestRepository.get_pending_requests_for_team(user.team_id)
        except Exception as e:
            pass
        table.setRowCount(len(requests))
        for row, req in enumerate(requests):
            # Only allow captain to approve competitors (not other captains/coaches)
            requester = None
            try:
                requester = UserRepository.get_user_by_id(req.requester_user_id)
            except Exception:
                pass
            if not requester:
                continue
            # Only show requests for roles below captain
            if self.user["role"] == "captain" and requester.role not in ["member", "competitor"]:
                continue
            table.setItem(row, 0, QTableWidgetItem(requester.name))
            table.setItem(row, 1, QTableWidgetItem(requester.email))
            table.setItem(row, 2, QTableWidgetItem(str(requester.role)))
            approve_btn = QPushButton("Approve")
            reject_btn = QPushButton("Reject")
            approve_btn.clicked.connect(lambda checked, rid=req.id: self._approve_join_request(rid))
            reject_btn.clicked.connect(lambda checked, rid=req.id: self._reject_join_request(rid))
            table.setCellWidget(row, 3, approve_btn)
            table.setCellWidget(row, 4, reject_btn)
        layout.addWidget(table)
        widget.setLayout(layout)
        return widget

    def _approve_join_request(self, request_id):
        from app.database.repositories import TeamJoinRequestRepository
        TeamJoinRequestRepository.approve_request(request_id)
        QMessageBox.information(self, "Success", "Request approved.")
        # Refresh the team members and join requests tabs
        self._refresh_tabs()

    def _reject_join_request(self, request_id):
        from app.database.repositories import TeamJoinRequestRepository
        TeamJoinRequestRepository.reject_request(request_id)
        QMessageBox.information(self, "Success", "Request rejected.")
        self._refresh_tabs()

    def _refresh_tabs(self):
        # Remove and re-add the Team Members and Join Requests tabs to refresh their content
        members_idx = self.tab_widget.indexOf(self.members_tab)
        join_idx = self.tab_widget.indexOf(self.join_requests_tab)
        self.tab_widget.removeTab(join_idx)
        self.tab_widget.removeTab(members_idx)
        self.members_tab = self._create_team_members_tab()
        self.join_requests_tab = self._create_join_requests_tab()
        self.tab_widget.insertTab(members_idx, self.members_tab, "Team Members")
        self.tab_widget.insertTab(join_idx, self.join_requests_tab, "Join Requests")
        self.tab_widget.insertTab(3, self.members_tab, "Team Members")
        self.tab_widget.removeTab(4)
        self.tab_widget.insertTab(4, self.join_requests_tab, "Join Requests")

    def _reject_join_request(self, request_id):
        from app.database.repositories import TeamJoinRequestRepository
        TeamJoinRequestRepository.reject_request(request_id)
        QMessageBox.information(self, "Rejected", "Request rejected.")
        self.join_requests_tab = self._create_join_requests_tab()
        self.tab_widget.removeTab(4)
        self.tab_widget.insertTab(4, self.join_requests_tab, "Join Requests")

    def _create_top_bar(self) -> QHBoxLayout:
        """Create the top navigation bar."""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        welcome_label = QLabel(f"Welcome, {self.user['name']} ({self.user['role'].capitalize()})")
        layout.addWidget(welcome_label)
        layout.addStretch()

        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self._handle_logout)
        layout.addWidget(logout_button)

        return layout

    def _update_team_status(self):
        """Update team membership status message."""
        try:
            user = UserRepository.get_user_by_id(self.user["id"])
            
            if user and user.team_id:
                team = user.team
                if user.is_approved:
                    self.status_label.setText(
                        f"✓ You are a member of team: {team.name} ({team.team_id})"
                    )
                    self.status_label.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
                else:
                    self.status_label.setText(
                        f"⏳ Pending approval for team: {team.name} ({team.team_id}). Your coach has been notified and will approve your request soon."
                    )
                    self.status_label.setStyleSheet("color: orange; font-weight: bold; padding: 5px;")
            else:
                self.status_label.setText(
                    "ℹ You are not yet part of a team. Please contact your coach to join or create a team."
                )
                self.status_label.setStyleSheet("color: blue; font-weight: bold; padding: 5px;")
        except Exception as e:
            self.status_label.setText(f"Error loading team status: {str(e)}")
            self.status_label.setStyleSheet("color: red; padding: 5px;")

    def _create_checklist_tab(self) -> QWidget:
        """Create checklist tab."""
        widget = QWidget()
        layout = QtQVBoxLayout()

        # Title
        title = QLabel("Checklist Hub")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        layout.addWidget(title)

        # Checklist list
        self.checklist_list = QListWidget()
        self._refresh_checklists()
        self.checklist_list.itemClicked.connect(self._on_checklist_selected)
        layout.addWidget(self.checklist_list)

        # Checklist details area
        self.checklist_details = QTextEdit()
        self.checklist_details.setReadOnly(True)
        self.checklist_details.setMinimumHeight(200)
        layout.addWidget(self.checklist_details)

        # Items table
        self.checklist_items_table = QTableWidget()
        self.checklist_items_table.setColumnCount(5)
        self.checklist_items_table.setHorizontalHeaderLabels(
            ["Item", "Status", "Notes", "Update", "Actions"]
        )
        layout.addWidget(self.checklist_items_table)

        # Buttons
        button_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._refresh_checklists)
        button_layout.addWidget(refresh_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def _create_readme_tab(self) -> QWidget:
        """Create README tab."""
        widget = QWidget()
        layout = QtQVBoxLayout()

        # Title
        title = QLabel("README Manager")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        layout.addWidget(title)

        # README list
        self.readme_list = QListWidget()
        self._refresh_readmes()
        self.readme_list.itemClicked.connect(self._on_readme_selected)
        layout.addWidget(self.readme_list)

        # README content
        self.readme_content = QTextEdit()
        self.readme_content.setReadOnly(True)
        layout.addWidget(self.readme_content)

        # Buttons
        button_layout = QHBoxLayout()
        create_button = QPushButton("Create README")
        create_button.clicked.connect(self._show_create_readme_dialog)
        button_layout.addWidget(create_button)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._refresh_readmes)
        button_layout.addWidget(refresh_button)

        edit_button = QPushButton("Edit Selected")
        edit_button.clicked.connect(self._show_edit_readme_dialog)
        button_layout.addWidget(edit_button)

        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self._handle_delete_readme)
        button_layout.addWidget(delete_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def _create_notes_tab(self) -> QWidget:
        """Create notes tab."""
        widget = QWidget()
        layout = QtQVBoxLayout()

        # Title
        title = QLabel("Notes System")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        layout.addWidget(title)

        # Notes list
        self.notes_list = QListWidget()
        self._refresh_notes()
        self.notes_list.itemClicked.connect(self._on_note_selected)
        layout.addWidget(self.notes_list)

        # Note content
        self.note_content = QTextEdit()
        self.note_content.setReadOnly(True)
        layout.addWidget(self.note_content)

        # Buttons
        button_layout = QHBoxLayout()
        create_button = QPushButton("Create Note")
        create_button.clicked.connect(self._show_create_note_dialog)
        button_layout.addWidget(create_button)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._refresh_notes)
        button_layout.addWidget(refresh_button)

        edit_button = QPushButton("Edit Selected")
        edit_button.clicked.connect(self._show_edit_note_dialog)
        button_layout.addWidget(edit_button)

        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self._handle_delete_note)
        button_layout.addWidget(delete_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def _refresh_checklists(self):
        """Refresh checklists list."""
        try:
            self.checklist_list.clear()
            checklists = ChecklistRepository.get_all_checklists()

            for checklist in checklists:
                item = QListWidgetItem(f"{checklist.title} ({checklist.category})")
                item.setData(Qt.UserRole, checklist.id)
                self.checklist_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load checklists: {str(e)}")

    def _refresh_readmes(self):
        """Refresh READMEs list."""
        try:
            self.readme_list.clear()
            if self.user.get("team_id"):
                readmes = ReadMeRepository.get_team_readmes(self.user["team_id"])

                for readme in readmes:
                    item = QListWidgetItem(f"{readme.title} ({readme.os_type})")
                    item.setData(Qt.UserRole, readme.id)
                    self.readme_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load READMEs: {str(e)}")

    def _refresh_notes(self):
        """Refresh notes list."""
        try:
            self.notes_list.clear()
            if self.user.get("team_id"):
                notes = NoteRepository.get_team_notes(self.user["team_id"])

                for note in notes:
                    item = QListWidgetItem(f"{note.title} ({note.note_type})")
                    item.setData(Qt.UserRole, note.id)
                    self.notes_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load notes: {str(e)}")

    def _on_checklist_selected(self, item: QListWidgetItem):
        """Handle checklist selection."""
        try:
            checklist_id = item.data(Qt.UserRole)
            checklist = ChecklistRepository.get_checklist_by_id(checklist_id)

            if checklist:
                # Show details
                details_text = f"Title: {checklist.title}\n"
                details_text += f"Category: {checklist.category}\n"
                details_text += f"Description: {checklist.description or 'N/A'}\n"
                self.checklist_details.setText(details_text)

                # Show items
                self.checklist_items_table.setRowCount(len(checklist.items))

                for row, item in enumerate(checklist.items):
                    status = ChecklistRepository.get_checklist_status(self.user["id"], item.id)
                    current_status = status.status if status else "pending"

                    self.checklist_items_table.setItem(row, 0, QTableWidgetItem(item.title))
                    self.checklist_items_table.setItem(row, 1, QTableWidgetItem(current_status.capitalize()))
                    self.checklist_items_table.setItem(row, 2, QTableWidgetItem(status.notes if status else ""))

                    # Status combo
                    status_combo = QComboBox()
                    status_combo.addItems(["Pending", "Completed", "Skipped"])
                    status_combo.setCurrentText(current_status.capitalize())
                    status_combo.currentTextChanged.connect(
                        lambda text, iid=item.id: self._update_item_status(iid, text)
                    )
                    self.checklist_items_table.setCellWidget(row, 3, status_combo)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load checklist details: {str(e)}")

    def _update_item_status(self, item_id: int, status_text: str):
        """Update checklist item status."""
        try:
            status = status_text.lower()
            ChecklistRepository.update_checklist_item_status(self.user["id"], item_id, status)
            AuditLogRepository.log_action(
                self.user["id"], "update_status", "checklist_item", item_id, f"Status changed to {status}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update status: {str(e)}")

    def _on_readme_selected(self, item: QListWidgetItem):
        """Handle README selection."""
        try:
            readme_id = item.data(Qt.UserRole)
            readme = ReadMeRepository.get_readme_by_id(readme_id)

            if readme:
                content = f"Title: {readme.title}\n"
                content += f"OS Type: {readme.os_type}\n"
                content += f"Author: {readme.author.name if readme.author else 'Unknown'}\n"
                content += f"Created: {readme.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                content += "\n--- Content ---\n"
                content += readme.content
                self.readme_content.setText(content)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load README: {str(e)}")

    def _on_note_selected(self, item: QListWidgetItem):
        """Handle note selection."""
        try:
            note_id = item.data(Qt.UserRole)
            note = NoteRepository.get_note_by_id(note_id)

            if note:
                content = f"Title: {note.title}\n"
                content += f"Type: {note.note_type}\n"
                content += f"Author: {note.author.name if note.author else 'Unknown'}\n"
                content += f"Created: {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                content += f"Encrypted: {'Yes' if note.is_encrypted else 'No'}\n"
                content += "\n--- Content ---\n"

                if note.is_encrypted:
                    try:
                        decrypted = EncryptionManager.decrypt_note(
                            note.content, self.user.get("password", ""), note.encryption_key_salt
                        )
                        content += decrypted
                    except Exception:
                        content += "[Unable to decrypt - incorrect password]"
                else:
                    content += note.content

                self.note_content.setText(content)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load note: {str(e)}")

    def _show_create_readme_dialog(self):
        """Show create README dialog."""
        dialog = CreateReadMeDialog(self, self.user)
        if dialog.exec() == QDialog.Accepted:
            self._refresh_readmes()

    def _show_edit_readme_dialog(self):
        """Show edit README dialog."""
        current_item = self.readme_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a README to edit.")
            return

        readme_id = current_item.data(Qt.UserRole)
        readme = ReadMeRepository.get_readme_by_id(readme_id)

        if readme:
            dialog = EditReadMeDialog(self, readme)
            if dialog.exec() == QDialog.Accepted:
                self._refresh_readmes()

    def _handle_delete_readme(self):
        """Handle delete README."""
        current_item = self.readme_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a README to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Delete this README?")
        if reply == QMessageBox.Yes:
            try:
                readme_id = current_item.data(Qt.UserRole)
                ReadMeRepository.delete_readme(readme_id)
                QMessageBox.information(self, "Success", "README deleted.")
                self._refresh_readmes()
                AuditLogRepository.log_action(
                    self.user["id"], "delete", "readme", readme_id, "README deleted"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete README: {str(e)}")

    def _show_create_note_dialog(self):
        """Show create note dialog."""
        dialog = CreateNoteDialog(self, self.user)
        if dialog.exec() == QDialog.Accepted:
            self._refresh_notes()

    def _show_edit_note_dialog(self):
        """Show edit note dialog."""
        current_item = self.notes_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a note to edit.")
            return

        note_id = current_item.data(Qt.UserRole)
        note = NoteRepository.get_note_by_id(note_id)

        if note:
            dialog = EditNoteDialog(self, note, self.user)
            if dialog.exec() == QDialog.Accepted:
                self._refresh_notes()

    def _handle_delete_note(self):
        """Handle delete note."""
        current_item = self.notes_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a note to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Delete this note?")
        if reply == QMessageBox.Yes:
            try:
                note_id = current_item.data(Qt.UserRole)
                NoteRepository.delete_note(note_id)
                QMessageBox.information(self, "Success", "Note deleted.")
                self._refresh_notes()
                AuditLogRepository.log_action(
                    self.user["id"], "delete", "note", note_id, "Note deleted"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete note: {str(e)}")

    def _handle_logout(self):
        """Handle logout."""
        reply = QMessageBox.question(self, "Confirm Logout", "Are you sure you want to logout?")
        if reply == QMessageBox.Yes:
            AuditLogRepository.log_action(self.user["id"], "logout", "auth", description="User logged out")
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
        QTextEdit {
            background-color: white;
        }
        QListWidget {
            background-color: white;
        }
        QTableWidget {
            background-color: white;
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


class CreateReadMeDialog(QDialog):
    """Dialog for creating a README."""

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Create README")
        self.setGeometry(200, 200, 600, 400)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI."""
        layout = QtQVBoxLayout()

        layout.addWidget(QLabel("Title:"))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("OS Type:"))
        self.os_input = QLineEdit()
        self.os_input.setPlaceholderText("e.g., Ubuntu 20.04, Windows 10")
        layout.addWidget(self.os_input)

        layout.addWidget(QLabel("Content:"))
        self.content_input = QTextEdit()
        layout.addWidget(self.content_input)

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
        title = self.title_input.text().strip()
        os_type = self.os_input.text().strip()
        content = self.content_input.toPlainText().strip()

        if not all([title, os_type, content]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            ReadMeRepository.create_readme(self.user["team_id"], self.user["id"], title, os_type, content)
            QMessageBox.information(self, "Success", "README created successfully.")
            AuditLogRepository.log_action(self.user["id"], "create", "readme", description=f"README '{title}' created")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create README: {str(e)}")


class EditReadMeDialog(QDialog):
    """Dialog for editing a README."""

    def __init__(self, parent=None, readme=None):
        super().__init__(parent)
        self.readme = readme
        self.setWindowTitle("Edit README")
        self.setGeometry(200, 200, 600, 400)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI."""
        layout = QtQVBoxLayout()

        layout.addWidget(QLabel("Title:"))
        self.title_input = QLineEdit()
        self.title_input.setText(self.readme.title)
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("OS Type:"))
        self.os_input = QLineEdit()
        self.os_input.setText(self.readme.os_type)
        layout.addWidget(self.os_input)

        layout.addWidget(QLabel("Content:"))
        self.content_input = QTextEdit()
        self.content_input.setText(self.readme.content)
        layout.addWidget(self.content_input)

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
        title = self.title_input.text().strip()
        os_type = self.os_input.text().strip()
        content = self.content_input.toPlainText().strip()

        if not all([title, os_type, content]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            ReadMeRepository.update_readme(self.readme.id, title, os_type, content)
            QMessageBox.information(self, "Success", "README updated successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update README: {str(e)}")


class CreateNoteDialog(QDialog):
    """Dialog for creating a note."""

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Create Note")
        self.setGeometry(200, 200, 600, 400)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI."""
        layout = QtQVBoxLayout()

        layout.addWidget(QLabel("Title:"))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Note Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["General", "Point Note", "Password Change"])
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel("Content:"))
        self.content_input = QTextEdit()
        layout.addWidget(self.content_input)

        self.encrypt_check = QCheckBox("Encrypt this note (requires password)")
        layout.addWidget(self.encrypt_check)

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
        title = self.title_input.text().strip()
        note_type = self.type_combo.currentText().lower().replace(" ", "_")
        content = self.content_input.toPlainText().strip()
        encrypt = self.encrypt_check.isChecked()

        if not all([title, content]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            if encrypt:
                # Ask for password
                password, ok = self._get_encryption_password()
                if not ok:
                    return

                encrypted_content, salt = EncryptionManager.encrypt_note(content, password)
                note = NoteRepository.create_note(
                    self.user["team_id"],
                    self.user["id"],
                    title,
                    encrypted_content,
                    note_type,
                    is_encrypted=True,
                )
                note.encryption_key_salt = salt
            else:
                NoteRepository.create_note(
                    self.user["team_id"],
                    self.user["id"],
                    title,
                    content,
                    note_type,
                    is_encrypted=False,
                )

            QMessageBox.information(self, "Success", "Note created successfully.")
            AuditLogRepository.log_action(
                self.user["id"], "create", "note", description=f"Note '{title}' created"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create note: {str(e)}")

    def _get_encryption_password(self) -> tuple:
        """Get password for encryption."""
        from PySide6.QtWidgets import QInputDialog

        password, ok = QInputDialog.getText(
            self,
            "Encryption Password",
            "Enter password to encrypt this note:",
            QLineEdit.Password,
        )
        return password, ok


class EditNoteDialog(QDialog):
    """Dialog for editing a note."""

    def __init__(self, parent=None, note=None, user=None):
        super().__init__(parent)
        self.note = note
        self.user = user
        self.setWindowTitle("Edit Note")
        self.setGeometry(200, 200, 600, 400)
        self._init_ui()

    def _init_ui(self):
        """Initialize UI."""
        layout = QtQVBoxLayout()

        layout.addWidget(QLabel("Title:"))
        self.title_input = QLineEdit()
        self.title_input.setText(self.note.title)
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Note Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["General", "Point Note", "Password Change"])
        self.type_combo.setCurrentText(self.note.note_type.replace("_", " ").title())
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel("Content:"))
        self.content_input = QTextEdit()

        if self.note.is_encrypted:
            self.content_input.setText("[Content is encrypted]")
            self.content_input.setReadOnly(True)
        else:
            self.content_input.setText(self.note.content)

        layout.addWidget(self.content_input)

        button_layout = QHBoxLayout()
        if not self.note.is_encrypted:
            save_btn = QPushButton("Save")
            save_btn.clicked.connect(self._handle_save)
            button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Close")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _handle_save(self):
        """Handle save button."""
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()

        if not all([title, content]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            NoteRepository.update_note(self.note.id, title, content)
            QMessageBox.information(self, "Success", "Note updated successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update note: {str(e)}")

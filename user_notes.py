"""Script for user-specific notes management."""

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
    QLineEdit,
    QDialog,
    QFormLayout,
    QComboBox,
)
from PySide6.QtCore import Qt, QSize, QDateTime
from PySide6.QtGui import QFont, QColor


class NotesWindow(QMainWindow):
    """Main window for user-specific notes."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberPatriot Notes")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet(self._get_stylesheet())
        self.notes_dir = Path("user_notes")
        self.notes_dir.mkdir(exist_ok=True)
        self.current_user = None
        self.current_notes = {}
        self.users = self._load_users()
        self._init_ui()

    def _load_users(self):
        """Load users from the database."""
        from db_config import get_connection, close_connection
        
        users = {}
        connection = get_connection()
        if not connection:
            return users
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, username FROM users WHERE is_active = 1 ORDER BY username")
            results = cursor.fetchall()
            for row in results:
                users[row['username']] = row['id']
            cursor.close()
        except Exception:
            pass
        finally:
            close_connection(connection)
        
        return users

    def _init_ui(self):
        """Initialize the main UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Personal Notes")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(title)

        # User selection
        user_layout = QHBoxLayout()
        user_label = QLabel("Select User:")
        user_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.user_combo = QComboBox()
        self.user_combo.currentTextChanged.connect(self._on_user_changed)
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_combo)
        user_layout.addStretch()
        main_layout.addLayout(user_layout)

        # Two-panel layout
        content_layout = QHBoxLayout()

        # Left panel: Notes list
        left_panel = QVBoxLayout()
        notes_label = QLabel("Notes:")
        notes_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_panel.addWidget(notes_label)

        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self._on_note_clicked)
        left_panel.addWidget(self.notes_list)

        # Right panel: Note content
        right_panel = QVBoxLayout()
        note_title_label = QLabel("Note Content:")
        note_title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_panel.addWidget(note_title_label)

        self.note_title_input = QLineEdit()
        self.note_title_input.setPlaceholderText("Note title")
        right_panel.addWidget(self.note_title_input)

        self.note_content = QTextEdit()
        self.note_content.setPlaceholderText("Type your note here...")
        right_panel.addWidget(self.note_content)

        # Action buttons
        button_layout = QHBoxLayout()
        new_btn = QPushButton("New Note")
        new_btn.clicked.connect(self._new_note)
        save_btn = QPushButton("Save Note")
        save_btn.clicked.connect(self._save_note)
        delete_btn = QPushButton("Delete Note")
        delete_btn.clicked.connect(self._delete_note)
        button_layout.addWidget(new_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(delete_btn)
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
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        bottom_button_layout.addStretch()
        bottom_button_layout.addWidget(close_btn)
        main_layout.addLayout(bottom_button_layout)

        central_widget.setLayout(main_layout)
        self._load_users_combo()

    def _load_users_combo(self):
        """Load users into the combo box."""
        self.user_combo.clear()
        if self.users:
            self.user_combo.addItems(sorted(self.users.keys()))
        else:
            self.user_combo.addItem("No users available")

    def _on_user_changed(self, username):
        """Handle user selection change."""
        if not username or username == "No users available":
            self.notes_list.clear()
            self.note_title_input.clear()
            self.note_content.setPlainText("")
            return
        
        self.current_user = username
        self._load_notes()

    def _load_notes(self):
        """Load notes for the selected user."""
        if not self.current_user:
            return

        self.notes_list.clear()
        user_notes_dir = self.notes_dir / self.current_user
        if not user_notes_dir.exists():
            user_notes_dir.mkdir(parents=True, exist_ok=True)
            return

        notes_files = list(user_notes_dir.glob("*.json"))
        self.current_notes = {}

        for note_file in sorted(notes_files):
            try:
                with open(note_file, "r") as f:
                    note_data = json.load(f)
                
                note_id = note_file.stem
                self.current_notes[note_id] = note_data
                
                title = note_data.get("title", "Untitled")
                timestamp = note_data.get("created", "Unknown date")
                
                display_text = f"{title} ({timestamp})"
                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.ItemDataRole.UserRole, note_id)
                self.notes_list.addItem(list_item)
            except Exception:
                pass

    def _on_note_clicked(self, item):
        """Handle note selection."""
        note_id = item.data(Qt.ItemDataRole.UserRole)
        if note_id in self.current_notes:
            note_data = self.current_notes[note_id]
            self.note_title_input.setText(note_data.get("title", ""))
            self.note_content.setPlainText(note_data.get("content", ""))

    def _new_note(self):
        """Create a new note."""
        if not self.current_user:
            QMessageBox.warning(self, "No User", "Please select a user first.")
            return

        self.note_title_input.clear()
        self.note_content.setPlainText("")
        self.notes_list.setCurrentRow(-1)

    def _save_note(self):
        """Save the current note."""
        if not self.current_user:
            QMessageBox.warning(self, "No User", "Please select a user first.")
            return

        title = self.note_title_input.text().strip()
        content = self.note_content.toPlainText().strip()

        if not title:
            QMessageBox.warning(self, "Validation Error", "Note title cannot be empty.")
            return

        if not content:
            QMessageBox.warning(self, "Validation Error", "Note content cannot be empty.")
            return

        # Create note ID based on title
        note_id = title.lower().replace(" ", "_")[:20]
        
        note_data = {
            "title": title,
            "content": content,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        user_notes_dir = self.notes_dir / self.current_user
        user_notes_dir.mkdir(parents=True, exist_ok=True)

        try:
            note_file = user_notes_dir / f"{note_id}.json"
            with open(note_file, "w") as f:
                json.dump(note_data, f, indent=2)
            
            QMessageBox.information(self, "Success", "Note saved successfully!")
            self._load_notes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save note: {str(e)}")

    def _delete_note(self):
        """Delete the selected note."""
        current_item = self.notes_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a note to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this note?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            note_id = current_item.data(Qt.ItemDataRole.UserRole)
            user_notes_dir = self.notes_dir / self.current_user
            note_file = user_notes_dir / f"{note_id}.json"

            try:
                if note_file.exists():
                    note_file.unlink()
                QMessageBox.information(self, "Success", "Note deleted successfully!")
                self._load_notes()
                self.note_title_input.clear()
                self.note_content.setPlainText("")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete note: {str(e)}")

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
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotesWindow()
    window.show()
    sys.exit(app.exec())

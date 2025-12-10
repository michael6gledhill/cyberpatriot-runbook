"""Script to create checklists with items, descriptions, and how-to instructions."""

import sys
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QComboBox,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont


class ChecklistItemDialog(QDialog):
    """Dialog for creating/editing checklist items."""

    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.setWindowTitle("Checklist Item")
        self.setGeometry(150, 150, 600, 500)
        self.setStyleSheet(self._get_stylesheet())
        self.item_data = item_data
        self._init_ui()

    def _init_ui(self):
        """Initialize the dialog UI."""
        layout = QFormLayout()

        # Item name
        name_label = QLabel("Item Name:")
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter the name of the checklist item")
        layout.addRow(name_label, self.name_input)

        # Item description
        desc_label = QLabel("Description:")
        desc_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter a brief description of the checklist item")
        self.desc_input.setMaximumHeight(100)
        layout.addRow(desc_label, self.desc_input)

        # How-to instructions
        howto_label = QLabel("How-To Instructions:")
        howto_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.howto_input = QTextEdit()
        self.howto_input.setPlaceholderText("Enter detailed step-by-step instructions on how to complete this item")
        layout.addRow(howto_label, self.howto_input)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

        self.setLayout(layout)

        # Load existing data if editing
        if self.item_data:
            self.name_input.setText(self.item_data.get("name", ""))
            self.desc_input.setText(self.item_data.get("description", ""))
            self.howto_input.setText(self.item_data.get("how_to", ""))

    def get_item_data(self):
        """Return the item data from the dialog."""
        name = self.name_input.text().strip()
        description = self.desc_input.toPlainText().strip()
        how_to = self.howto_input.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Item name cannot be empty.")
            return None

        if not description:
            QMessageBox.warning(self, "Validation Error", "Description cannot be empty.")
            return None

        if not how_to:
            QMessageBox.warning(self, "Validation Error", "How-to instructions cannot be empty.")
            return None

        return {
            "name": name,
            "description": description,
            "how_to": how_to,
        }

    def _get_stylesheet(self) -> str:
        """Return the stylesheet for the dialog."""
        return """
        QDialog {
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
        QTextEdit {
            padding: 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: white;
        }
        QTextEdit:focus {
            border: 2px solid #4CAF50;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 4px;
            padding: 10px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        """


class CreateChecklistWindow(QMainWindow):
    """Main window for creating checklists."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberPatriot Checklist Creator")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet(self._get_stylesheet())
        self.checklist_items = []
        self.checklists_dir = Path("checklists")
        self.checklists_dir.mkdir(exist_ok=True)
        self.teams = self._load_teams()
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
            cursor.execute("SELECT id, name, team_code FROM teams ORDER BY name")
            results = cursor.fetchall()
            for row in results:
                teams[row['name']] = row['id']
            cursor.close()
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to load teams: {str(e)}")
        finally:
            close_connection(connection)
        
        return teams

    def _init_ui(self):
        """Initialize the main UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Title
        title = QLabel("Create a New Checklist")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Team selection
        team_layout = QHBoxLayout()
        team_label = QLabel("Assign to Team:")
        team_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.team_combo = QComboBox()
        if self.teams:
            self.team_combo.addItems(sorted(self.teams.keys()))
        else:
            self.team_combo.addItem("No teams available")
        team_layout.addWidget(team_label)
        team_layout.addWidget(self.team_combo)
        team_layout.addStretch()
        layout.addLayout(team_layout)

        # Checklist name
        name_layout = QHBoxLayout()
        name_label = QLabel("Checklist Name:")
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.checklist_name = QLineEdit()
        self.checklist_name.setPlaceholderText("Enter the name of the checklist (e.g., 'Windows Hardening')")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.checklist_name)
        layout.addLayout(name_layout)

        # Items table
        items_label = QLabel("Checklist Items:")
        items_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(items_label)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(3)
        self.items_table.setHorizontalHeaderLabels(["Item Name", "Description", "How-To"])
        self.items_table.horizontalHeader().setStretchLastSection(True)
        self.items_table.setColumnWidth(0, 150)
        self.items_table.setColumnWidth(1, 300)
        layout.addWidget(self.items_table)

        # Buttons for item management
        item_button_layout = QHBoxLayout()
        add_item_btn = QPushButton("Add Item")
        add_item_btn.clicked.connect(self._add_item)
        edit_item_btn = QPushButton("Edit Item")
        edit_item_btn.clicked.connect(self._edit_item)
        delete_item_btn = QPushButton("Delete Item")
        delete_item_btn.clicked.connect(self._delete_item)
        item_button_layout.addWidget(add_item_btn)
        item_button_layout.addWidget(edit_item_btn)
        item_button_layout.addWidget(delete_item_btn)
        item_button_layout.addStretch()
        layout.addLayout(item_button_layout)

        # Buttons for checklist management
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Checklist")
        save_btn.clicked.connect(self._save_checklist)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        central_widget.setLayout(layout)

    def _add_item(self):
        """Add a new checklist item."""
        dialog = ChecklistItemDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item_data = dialog.get_item_data()
            if item_data:
                self.checklist_items.append(item_data)
                self._refresh_table()

    def _edit_item(self):
        """Edit the selected checklist item."""
        current_row = self.items_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select an item to edit.")
            return

        dialog = ChecklistItemDialog(self, self.checklist_items[current_row])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item_data = dialog.get_item_data()
            if item_data:
                self.checklist_items[current_row] = item_data
                self._refresh_table()

    def _delete_item(self):
        """Delete the selected checklist item."""
        current_row = self.items_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select an item to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{self.checklist_items[current_row]['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.checklist_items.pop(current_row)
            self._refresh_table()

    def _refresh_table(self):
        """Refresh the items table."""
        self.items_table.setRowCount(len(self.checklist_items))
        for row, item in enumerate(self.checklist_items):
            name_item = QTableWidgetItem(item["name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            desc_item = QTableWidgetItem(item["description"][:50] + "..." if len(item["description"]) > 50 else item["description"])
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            howto_item = QTableWidgetItem(item["how_to"][:50] + "..." if len(item["how_to"]) > 50 else item["how_to"])
            howto_item.setFlags(howto_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.items_table.setItem(row, 0, name_item)
            self.items_table.setItem(row, 1, desc_item)
            self.items_table.setItem(row, 2, howto_item)

    def _save_checklist(self):
        """Save the checklist to a JSON file."""
        checklist_name = self.checklist_name.text().strip()
        if not checklist_name:
            QMessageBox.warning(self, "Validation Error", "Checklist name cannot be empty.")
            return

        if not self.checklist_items:
            QMessageBox.warning(self, "Validation Error", "Checklist must contain at least one item.")
            return

        selected_team = self.team_combo.currentText()
        if not selected_team or selected_team == "No teams available":
            QMessageBox.warning(self, "Validation Error", "Please select a team for this checklist.")
            return

        team_id = self.teams.get(selected_team)
        if not team_id:
            QMessageBox.warning(self, "Validation Error", "Invalid team selected.")
            return

        checklist_data = {
            "name": checklist_name,
            "team_id": team_id,
            "team_name": selected_team,
            "items": self.checklist_items,
        }

        filename = self.checklists_dir / f"{checklist_name.lower().replace(' ', '_')}.json"
        try:
            with open(filename, "w") as f:
                json.dump(checklist_data, f, indent=2)
            QMessageBox.information(self, "Success", f"Checklist saved to {filename}")
            self._reset_form()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save checklist: {str(e)}")

    def _reset_form(self):
        """Reset the form for a new checklist."""
        self.checklist_name.clear()
        self.checklist_items.clear()
        if self.team_combo.count() > 0:
            self.team_combo.setCurrentIndex(0)
        self._refresh_table()

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
        QTextEdit {
            padding: 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: white;
        }
        QTextEdit:focus {
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
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CreateChecklistWindow()
    window.show()
    sys.exit(app.exec())

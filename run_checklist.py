"""Script to run and complete checklists."""

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
    QPushButton,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QComboBox,
    QScrollArea,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor


class RunChecklistWindow(QMainWindow):
    """Main window for running checklists."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberPatriot Checklist Runner")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(self._get_stylesheet())
        self.checklists_dir = Path("checklists")
        self.current_checklist = None
        self.checklist_items = []
        self.item_statuses = {}
        self.item_viewed = {}  # Track which items have been viewed
        self.current_item_index = 0
        self.teams = self._load_teams()
        self._init_ui()
        self._load_teams_combo()

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
        except Exception as e:
            pass
        finally:
            close_connection(connection)
        
        return teams

    def _init_ui(self):
        """Initialize the main UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("CyberPatriot Checklist Runner")
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

        # Checklist selection
        selection_layout = QHBoxLayout()
        selection_label = QLabel("Select Checklist:")
        selection_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.checklist_combo = QComboBox()
        self.checklist_combo.currentTextChanged.connect(self._on_checklist_changed)
        selection_layout.addWidget(selection_label)
        selection_layout.addWidget(self.checklist_combo)
        selection_layout.addStretch()
        main_layout.addLayout(selection_layout)

        # Two-panel layout
        content_layout = QHBoxLayout()

        # Left panel: Items list
        left_panel = QVBoxLayout()
        items_label = QLabel("Checklist Items:")
        items_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_panel.addWidget(items_label)

        self.items_list = QListWidget()
        self.items_list.itemClicked.connect(self._on_item_clicked)
        left_panel.addWidget(self.items_list)

        # Right panel: Item details
        right_panel = QVBoxLayout()
        item_title_label = QLabel("Item Details:")
        item_title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_panel.addWidget(item_title_label)

        # Item name
        self.item_name_label = QLabel("")
        self.item_name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        right_panel.addWidget(self.item_name_label)

        # Description section
        desc_label = QLabel("Description:")
        desc_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_panel.addWidget(desc_label)

        self.item_description = QTextEdit()
        self.item_description.setReadOnly(True)
        self.item_description.setMaximumHeight(100)
        right_panel.addWidget(self.item_description)

        # How-to section
        howto_label = QLabel("How-To Instructions:")
        howto_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_panel.addWidget(howto_label)

        self.item_howto = QTextEdit()
        self.item_howto.setReadOnly(True)
        right_panel.addWidget(self.item_howto)

        # Status buttons
        status_label = QLabel("Mark as:")
        status_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_panel.addWidget(status_label)

        button_layout = QHBoxLayout()
        self.not_done_btn = QPushButton("Not Done")
        self.not_done_btn.setStyleSheet(self._get_button_stylesheet("#FF9800"))
        self.not_done_btn.clicked.connect(self._mark_not_done)

        self.complete_btn = QPushButton("✓ Complete")
        self.complete_btn.setStyleSheet(self._get_button_stylesheet("#4CAF50"))
        self.complete_btn.clicked.connect(self._mark_complete)

        self.skipped_btn = QPushButton("⊘ Skipped")
        self.skipped_btn.setStyleSheet(self._get_button_stylesheet("#2196F3"))
        self.skipped_btn.clicked.connect(self._mark_skipped)

        button_layout.addWidget(self.not_done_btn)
        button_layout.addWidget(self.complete_btn)
        button_layout.addWidget(self.skipped_btn)
        right_panel.addLayout(button_layout)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self._go_previous)
        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self._go_next)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        right_panel.addLayout(nav_layout)

        # Progress info
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #666666; font-style: italic;")
        right_panel.addWidget(self.progress_label)

        right_panel.addStretch()

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
        refresh_btn.clicked.connect(self._load_checklists)
        export_btn = QPushButton("Export Report")
        export_btn.clicked.connect(self._export_report)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        bottom_button_layout.addWidget(refresh_btn)
        bottom_button_layout.addWidget(export_btn)
        bottom_button_layout.addStretch()
        bottom_button_layout.addWidget(close_btn)
        main_layout.addLayout(bottom_button_layout)

        central_widget.setLayout(main_layout)

    def _load_teams_combo(self):
        """Load teams into the team combo box."""
        self.team_combo.clear()
        if self.teams:
            self.team_combo.addItems(sorted(self.teams.keys()))
        else:
            self.team_combo.addItem("No teams available")

    def _on_team_changed(self, team_name):
        """Handle team selection change."""
        if not team_name or team_name == "No teams available":
            self.checklist_combo.clear()
            self.progress_label.setText("Please select a valid team")
            return
        
        self._load_checklists()

    def _load_checklists(self):
        """Load checklists for the selected team."""
        selected_team = self.team_combo.currentText()
        if not selected_team or selected_team == "No teams available":
            self.checklist_combo.clear()
            return

        if not self.checklists_dir.exists():
            self.checklists_dir.mkdir(exist_ok=True)
            return

        self.checklist_combo.clear()
        checklist_files = list(self.checklists_dir.glob("*.json"))

        if not checklist_files:
            self.progress_label.setText("No checklists found for this team. Create one using create_checklist.py")
            return

        # Filter checklists by selected team
        team_id = self.teams.get(selected_team)
        team_checklists = []

        for file in checklist_files:
            try:
                with open(file, "r") as f:
                    checklist_data = json.load(f)
                    if checklist_data.get("team_id") == team_id:
                        team_checklists.append((file.stem, file))
            except Exception:
                pass

        if not team_checklists:
            self.progress_label.setText("No checklists found for this team")
            return

        for name, file_path in team_checklists:
            self.checklist_combo.addItem(name, file_path)

    def _on_checklist_changed(self, checklist_name):
        """Handle checklist selection change."""
        if not checklist_name:
            return

        file_path = self.checklist_combo.currentData()
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                checklist_data = json.load(f)

            self.current_checklist = checklist_data
            self.checklist_items = checklist_data.get("items", [])
            self.item_statuses = {i: "incomplete" for i in range(len(self.checklist_items))}
            self.item_viewed = {i: False for i in range(len(self.checklist_items))}  # Initialize as not viewed
            self.current_item_index = 0
            self._refresh_items_list()
            self._display_current_item()
            self._mark_item_viewed(0)  # Mark first item as viewed
            self._update_progress_label()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load checklist: {str(e)}")

    def _refresh_items_list(self):
        """Refresh the items list display."""
        self.items_list.clear()

        for idx, item in enumerate(self.checklist_items):
            status = self.item_statuses.get(idx, "incomplete")
            viewed = self.item_viewed.get(idx, False)
            item_text = item["name"]
            
            # Add status indicator to item name
            if status == "complete":
                status_indicator = "✓"
                text_color = QColor("#4CAF50")  # Green text
            elif status == "skipped":
                status_indicator = "⊘"
                text_color = QColor("#2196F3")  # Blue text
            elif status == "incomplete" and not viewed:
                status_indicator = "●"  # White dot with black outline
                text_color = QColor("#000000")  # Black text
            elif status == "incomplete" and viewed:
                status_indicator = "●"  # Red dot
                text_color = QColor("#F44336")  # Red text
            else:
                status_indicator = "○"
                text_color = QColor("#333333")  # Dark gray

            display_text = f"{status_indicator} {item_text}"

            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, idx)
            list_item.setForeground(text_color)

            self.items_list.addItem(list_item)

        # Select current item
        if 0 <= self.current_item_index < len(self.checklist_items):
            self.items_list.setCurrentRow(self.current_item_index)

    def _display_current_item(self):
        """Display the current item in the details panel."""
        if not self.checklist_items or self.current_item_index < 0 or self.current_item_index >= len(self.checklist_items):
            self.item_name_label.setText("")
            self.item_description.setPlainText("")
            self.item_howto.setPlainText("")
            return

        item = self.checklist_items[self.current_item_index]
        self.item_name_label.setText(item["name"])
        self.item_description.setPlainText(item["description"])
        self.item_howto.setPlainText(item["how_to"])

        # Update button states
        self._update_navigation_buttons()

    def _on_item_clicked(self, item):
        """Handle item click to change current item."""
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx is not None and 0 <= idx < len(self.checklist_items):
            self.current_item_index = idx
            self._display_current_item()
            self._mark_item_viewed(idx)
            self._update_progress_label()

    def _mark_item_viewed(self, idx):
        """Mark an item as viewed."""
        if 0 <= idx < len(self.checklist_items):
            self.item_viewed[idx] = True
            self._refresh_items_list()

    def _mark_complete(self):
        """Mark current item as complete and go to next."""
        if 0 <= self.current_item_index < len(self.checklist_items):
            self.item_statuses[self.current_item_index] = "complete"
            self._refresh_items_list()
            self._go_next()

    def _mark_skipped(self):
        """Mark current item as skipped and go to next."""
        if 0 <= self.current_item_index < len(self.checklist_items):
            self.item_statuses[self.current_item_index] = "skipped"
            self._refresh_items_list()
            self._go_next()

    def _mark_not_done(self):
        """Mark current item as not done and go to next."""
        if 0 <= self.current_item_index < len(self.checklist_items):
            self.item_statuses[self.current_item_index] = "incomplete"
            self._refresh_items_list()
            self._go_next()

    def _go_next(self):
        """Move to the next item."""
        if self.current_item_index < len(self.checklist_items) - 1:
            self.current_item_index += 1
            self._display_current_item()
            self._mark_item_viewed(self.current_item_index)
            self._update_progress_label()

    def _go_previous(self):
        """Move to the previous item."""
        if self.current_item_index > 0:
            self.current_item_index -= 1
            self._display_current_item()
            self._mark_item_viewed(self.current_item_index)
            self._update_progress_label()

    def _update_navigation_buttons(self):
        """Update the enabled state of navigation buttons."""
        self.prev_btn.setEnabled(self.current_item_index > 0)
        self.next_btn.setEnabled(self.current_item_index < len(self.checklist_items) - 1)

    def _update_progress_label(self):
        """Update the progress label."""
        if not self.checklist_items:
            self.progress_label.setText("")
            return
        
        progress_text = f"Item {self.current_item_index + 1} of {len(self.checklist_items)}"
        self.progress_label.setText(progress_text)

    def _export_report(self):
        """Export the checklist progress as a report."""
        if not self.current_checklist:
            QMessageBox.warning(self, "No Checklist", "Please select a checklist first.")
            return

        report_lines = [
            f"Checklist Report: {self.current_checklist.get('name', 'Unknown')}",
            "=" * 60,
            "",
        ]

        complete_count = 0
        skipped_count = 0
        incomplete_count = 0

        for idx, item in enumerate(self.checklist_items):
            status = self.item_statuses.get(idx, "incomplete")
            status_str = "✓ COMPLETE" if status == "complete" else ("⊘ SKIPPED" if status == "skipped" else "○ INCOMPLETE")

            report_lines.append(f"[{status_str}] {item['name']}")
            report_lines.append(f"  Description: {item['description']}")
            report_lines.append("")

            if status == "complete":
                complete_count += 1
            elif status == "skipped":
                skipped_count += 1
            else:
                incomplete_count += 1

        # Summary
        total = len(self.checklist_items)
        report_lines.append("=" * 60)
        report_lines.append("SUMMARY")
        report_lines.append(f"Total Items: {total}")
        report_lines.append(f"Completed: {complete_count} ({complete_count*100//total}%)")
        report_lines.append(f"Skipped: {skipped_count} ({skipped_count*100//total}%)")
        report_lines.append(f"Incomplete: {incomplete_count} ({incomplete_count*100//total}%)")

        report_text = "\n".join(report_lines)

        # Show report in message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Checklist Report")
        msg_box.setText("Report generated successfully!")
        msg_box.setDetailedText(report_text)
        msg_box.setStyleSheet(self._get_stylesheet())
        msg_box.exec()

    def _get_button_stylesheet(self, color: str) -> str:
        """Return stylesheet for colored status buttons."""
        return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 4px;
            padding: 10px;
        }}
        QPushButton:hover {{
            opacity: 0.8;
        }}
        QPushButton:pressed {{
            opacity: 0.6;
        }}
        """

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
        QPushButton:disabled {
            background-color: #cccccc;
            color: #999999;
        }
        QListWidget {
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: white;
            font-family: monospace;
        }
        QListWidget::item {
            padding: 4px;
        }
        QListWidget::item:hover {
            background-color: #e8f5e9;
        }
        QListWidget::item:selected {
            background-color: #4CAF50;
            color: white;
        }
        QMessageBox {
            background-color: #f5f5f5;
        }
        QMessageBox QLabel {
            color: #333333;
        }
        QTextEdit {
            background-color: white;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 8px;
        }
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RunChecklistWindow()
    window.show()
    sys.exit(app.exec())

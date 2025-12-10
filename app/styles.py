"""
Simplified stylesheet module for clean, professional UI.
Uses only Qt Style Sheet (QSS) compatible properties.
"""

STYLESHEET = """
    QWidget {
        background-color: #f5f5f5;
        color: #333333;
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 11px;
    }

    QMainWindow, QStackedWidget {
        background-color: #ffffff;
    }

    /* Labels */
    QLabel {
        color: #333333;
    }

    QLabel#title {
        font-size: 24px;
        font-weight: bold;
        color: #1e40af;
    }

    QLabel#subtitle {
        font-size: 11px;
        color: #666666;
    }

    QLabel#status-success {
        color: #15803d;
        font-weight: bold;
    }

    QLabel#status-error {
        color: #dc2626;
        font-weight: bold;
    }

    QLabel#status-info {
        color: #0284c7;
        font-weight: bold;
    }

    /* Line Edits */
    QLineEdit {
        border: 1px solid #d1d5db;
        border-radius: 4px;
        padding: 8px;
        background-color: #ffffff;
        color: #333333;
    }

    QLineEdit:focus {
        border: 2px solid #1e40af;
        background-color: #f0f9ff;
    }

    /* ComboBox */
    QComboBox {
        border: 1px solid #d1d5db;
        border-radius: 4px;
        padding: 6px;
        background-color: #ffffff;
        color: #333333;
    }

    QComboBox:focus {
        border: 2px solid #1e40af;
        background-color: #f0f9ff;
    }

    QComboBox QAbstractItemView {
        border: 1px solid #d1d5db;
        background-color: #ffffff;
        color: #333333;
        selection-background-color: #1e40af;
        selection-color: #ffffff;
    }

    /* Buttons */
    QPushButton {
        background-color: #1e40af;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 600;
        min-height: 36px;
    }

    QPushButton:hover {
        background-color: #1e3a8a;
    }

    QPushButton:pressed {
        background-color: #1e3a8a;
    }

    QPushButton:disabled {
        background-color: #d1d5db;
        color: #9ca3af;
    }

    QPushButton#secondary {
        background-color: #6b7280;
    }

    QPushButton#secondary:hover {
        background-color: #4b5563;
    }

    QPushButton#danger {
        background-color: #dc2626;
    }

    QPushButton#danger:hover {
        background-color: #b91c1c;
    }

    /* ScrollBar */
    QScrollBar:vertical {
        border: none;
        background-color: #f5f5f5;
        width: 10px;
    }

    QScrollBar::handle:vertical {
        background-color: #cbd5e1;
        border-radius: 5px;
        min-height: 20px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #94a3b8;
    }

    QScrollBar:horizontal {
        border: none;
        background-color: #f5f5f5;
        height: 10px;
    }

    QScrollBar::handle:horizontal {
        background-color: #cbd5e1;
        border-radius: 5px;
        min-width: 20px;
    }

    QScrollBar::handle:horizontal:hover {
        background-color: #94a3b8;
    }

    /* Frame */
    QFrame {
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        background-color: #ffffff;
    }

    QFrame#card {
        padding: 20px;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        background-color: #ffffff;
    }

    /* GroupBox */
    QGroupBox {
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: 600;
        color: #1e40af;
    }

    /* TabWidget */
    QTabWidget::pane {
        border: 1px solid #e5e7eb;
    }

    QTabBar::tab {
        background-color: #f3f4f6;
        color: #6b7280;
        border: 1px solid #e5e7eb;
        padding: 6px 14px;
        margin-right: 2px;
        font-weight: 500;
    }

    QTabBar::tab:selected {
        background-color: #1e40af;
        color: #ffffff;
        border-color: #1e40af;
    }

    QTabBar::tab:hover {
        background-color: #e0e7ff;
        color: #1e40af;
    }

    /* TableWidget */
    QTableWidget {
        border: 1px solid #e5e7eb;
        background-color: #ffffff;
        gridline-color: #f3f4f6;
    }

    QTableWidget::item {
        padding: 4px;
        color: #333333;
    }

    QTableWidget::item:selected {
        background-color: #dbeafe;
        color: #1e40af;
    }

    QHeaderView::section {
        background-color: #f3f4f6;
        color: #1f2937;
        padding: 6px;
        border: none;
        font-weight: 600;
        border-bottom: 1px solid #e5e7eb;
    }

    /* Spinbox */
    QSpinBox, QDoubleSpinBox {
        border: 1px solid #d1d5db;
        border-radius: 4px;
        padding: 6px;
        background-color: #ffffff;
        color: #333333;
    }

    QSpinBox:focus, QDoubleSpinBox:focus {
        border: 2px solid #1e40af;
        background-color: #f0f9ff;
    }

    /* Checkbox and Radio */
    QCheckBox, QRadioButton {
        color: #333333;
        spacing: 6px;
    }

    QCheckBox::indicator, QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #cbd5e1;
        background-color: #ffffff;
    }

    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #1e40af;
        border: 1px solid #1e40af;
    }

    QCheckBox::indicator:hover, QRadioButton::indicator:hover {
        border: 1px solid #1e40af;
    }

    /* Scroll Area */
    QScrollArea {
        border: none;
        background-color: #ffffff;
    }
"""

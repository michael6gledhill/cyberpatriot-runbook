"""
Stylesheet module for professional, modern UI appearance.
Includes colors, fonts, and component styles inspired by modern design systems.
"""

STYLESHEET = """
    QWidget {
        background-color: #f5f5f5;
        color: #333333;
        font-family: "Segoe UI", Arial, sans-serif;
    }

    QMainWindow, QStackedWidget {
        background-color: #ffffff;
    }

    /* Labels */
    QLabel {
        color: #333333;
    }

    QLabel#title {
        font-size: 28px;
        font-weight: bold;
        color: #1e40af;
        margin-bottom: 10px;
    }

    QLabel#subtitle {
        font-size: 14px;
        color: #666666;
        margin-bottom: 20px;
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
        border: 2px solid #e5e7eb;
        border-radius: 6px;
        padding: 10px 12px;
        font-size: 13px;
        background-color: #ffffff;
        color: #333333;
        selection-background-color: #1e40af;
    }

    QLineEdit:focus {
        border: 2px solid #1e40af;
        background-color: #f0f9ff;
    }

    QLineEdit::placeholder {
        color: #9ca3af;
    }

    /* ComboBox */
    QComboBox {
        border: 2px solid #e5e7eb;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        background-color: #ffffff;
        color: #333333;
    }

    QComboBox:focus {
        border: 2px solid #1e40af;
        background-color: #f0f9ff;
    }

    QComboBox::drop-down {
        border: none;
        width: 30px;
    }

    QComboBox QAbstractItemView {
        border: 1px solid #e5e7eb;
        border-radius: 4px;
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
        border-radius: 6px;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
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
        color: #ffffff;
    }

    QPushButton#secondary:hover {
        background-color: #4b5563;
    }

    QPushButton#danger {
        background-color: #dc2626;
        color: #ffffff;
    }

    QPushButton#danger:hover {
        background-color: #b91c1c;
    }

    /* Scroll Area */
    QScrollArea {
        border: none;
        background-color: #ffffff;
    }

    QScrollBar:vertical {
        border: none;
        background-color: #f5f5f5;
        width: 12px;
        border-radius: 6px;
    }

    QScrollBar::handle:vertical {
        background-color: #cbd5e1;
        border-radius: 6px;
        min-height: 20px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #94a3b8;
    }

    QScrollBar:horizontal {
        border: none;
        background-color: #f5f5f5;
        height: 12px;
        border-radius: 6px;
    }

    QScrollBar::handle:horizontal {
        background-color: #cbd5e1;
        border-radius: 6px;
        min-width: 20px;
    }

    QScrollBar::handle:horizontal:hover {
        background-color: #94a3b8;
    }

    /* Frame */
    QFrame {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        background-color: #ffffff;
    }

    QFrame#card {
        padding: 20px;
    }

    /* Group Box */
    QGroupBox {
        border: 2px solid #e5e7eb;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 15px;
        font-weight: 600;
        color: #1e40af;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }

    /* Tab Widget */
    QTabWidget::pane {
        border: 1px solid #e5e7eb;
        border-radius: 6px;
    }

    QTabBar::tab {
        background-color: #f3f4f6;
        color: #6b7280;
        border: 1px solid #e5e7eb;
        padding: 8px 16px;
        margin-right: 2px;
        border-radius: 4px 4px 0 0;
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

    /* Table Widget */
    QTableWidget {
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        background-color: #ffffff;
        gridline-color: #f3f4f6;
    }

    QTableWidget::item {
        padding: 8px;
        color: #333333;
    }

    QTableWidget::item:selected {
        background-color: #dbeafe;
        color: #1e40af;
    }

    QHeaderView::section {
        background-color: #f3f4f6;
        color: #1f2937;
        padding: 8px;
        border: none;
        font-weight: 600;
        border-bottom: 2px solid #e5e7eb;
    }

    /* Spinbox and other widgets */
    QSpinBox, QDoubleSpinBox {
        border: 2px solid #e5e7eb;
        border-radius: 6px;
        padding: 8px 12px;
        background-color: #ffffff;
        color: #333333;
    }

    QSpinBox:focus, QDoubleSpinBox:focus {
        border: 2px solid #1e40af;
        background-color: #f0f9ff;
    }

    QCheckBox, QRadioButton {
        color: #333333;
        spacing: 6px;
    }

    QCheckBox::indicator, QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border-radius: 3px;
        border: 2px solid #cbd5e1;
        background-color: #ffffff;
    }

    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #1e40af;
        border: 2px solid #1e40af;
    }

    QCheckBox::indicator:hover, QRadioButton::indicator:hover {
        border: 2px solid #1e40af;
    }
"""

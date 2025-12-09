"""CyberPatriot Runbook Application Entry Point."""

import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox

from app.database import init_db
from app.gui.main_window import MainWindow


def main():
    """Main application entry point."""
    try:
        # Initialize database
        db_url = os.getenv(
            "DATABASE_URL",
            "mysql+pymysql://root:h0gBog89!@localhost:3306/cyberpatriot_runbook"
        )

        print(f"Initializing database: {db_url}")
        init_db(db_url)
        print("Database initialized successfully!")

        # Create application
        app = QApplication(sys.argv)

        # Create and show main window
        main_window = MainWindow()
        main_window.show()

        # Run application
        sys.exit(app.exec())

    except Exception as e:
        print(f"Error starting application: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

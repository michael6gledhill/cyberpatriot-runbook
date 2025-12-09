"""
Installation and Setup Guide for CyberPatriot Runbook
"""

import os
import sys
from pathlib import Path


def setup_environment():
    """Set up the application environment."""
    print("=" * 60)
    print("CyberPatriot Runbook - Setup")
    print("=" * 60)

    # Check Python version
    if sys.version_info < (3, 9):
        print("ERROR: Python 3.9+ is required.")
        sys.exit(1)

    print(f"✓ Python version: {sys.version}")

    # Create necessary directories
    print("\nCreating directory structure...")
    required_dirs = [
        "app/gui/dialogs",
        "app/controllers",
        "app/models",
        "app/database",
        "app/security",
        "resources",
        "alembic/versions",
    ]

    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")

    print("\n" + "=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Configure MySQL database in config.py")
    print("3. Set DATABASE_URL environment variable (optional)")
    print("4. Run: python main.py")


if __name__ == "__main__":
    setup_environment()

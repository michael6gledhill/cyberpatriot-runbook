#!/usr/bin/env python3
"""
CyberPatriot Runbook - Dependency Validation Script

This script validates that all required dependencies are installed and working.
"""

import sys
import importlib
from pathlib import Path


def check_python_version():
    """Check Python version is 3.9+"""
    print("Checking Python version...")
    if sys.version_info < (3, 9):
        print(f"  ✗ Python 3.9+ required, got {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True


def check_dependency(package_name, import_name=None, version_attr="__version__"):
    """Check if a dependency is installed."""
    if import_name is None:
        import_name = package_name

    print(f"Checking {package_name}...", end=" ")
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, version_attr, "unknown")
        print(f"✓ ({version})")
        return True
    except ImportError:
        print(f"✗ Not installed")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def check_required_files():
    """Check that required project files exist."""
    print("\nChecking required files...")
    required_files = [
        "main.py",
        "config.py",
        "requirements.txt",
        "database_setup.sql",
        "README.md",
        "QUICKSTART.md",
        "SETUP.md",
        "ARCHITECTURE.md",
    ]

    required_dirs = [
        "app",
        "app/gui",
        "app/controllers",
        "app/models",
        "app/database",
        "app/security",
        "alembic",
    ]

    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} missing")
            all_exist = False

    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ missing")
            all_exist = False

    return all_exist


def check_database_connection():
    """Check MySQL connectivity."""
    print("\nChecking MySQL connection...")
    try:
        import mysql.connector

        print("  ✓ PyMySQL/mysql-connector available")
        return True
    except ImportError:
        print("  ⚠ MySQL driver not available (needed for runtime)")
        return False


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("CyberPatriot Runbook - Dependency Validation")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version()),
    ]

    print("\nChecking Python dependencies...")
    dependencies = [
        ("PySide6", "PySide6"),
        ("SQLAlchemy", "sqlalchemy"),
        ("PyMySQL", "pymysql"),
        ("bcrypt", "bcrypt"),
        ("cryptography", "cryptography"),
        ("Alembic", "alembic"),
        ("python-dotenv", "dotenv"),
    ]

    all_deps_ok = True
    for pkg_name, import_name in dependencies:
        if not check_dependency(pkg_name, import_name):
            all_deps_ok = False

    checks.append(("Dependencies", all_deps_ok))

    files_ok = check_required_files()
    checks.append(("Project Files", files_ok))

    db_ok = check_database_connection()
    checks.append(("Database Support", db_ok))

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    all_ok = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
        if not result:
            all_ok = False

    print("=" * 60)

    if all_ok:
        print("\n✓ All checks passed! Application is ready to run.")
        print("\nTo start the application:")
        print("  python main.py")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nTo install dependencies:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())

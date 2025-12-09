"""
CyberPatriot Runbook - Team Security Checklist Management Application

A comprehensive desktop application for managing team security checklists,
documentation, and notes during CyberPatriot competitions.

Requirements:
- Python 3.9+
- MySQL 5.7+ or MariaDB
- PySide6 for GUI
- SQLAlchemy for ORM
- bcrypt for password hashing
- cryptography for sensitive data encryption

Installation:
1. Install Python dependencies:
   pip install -r requirements.txt

2. Set up MySQL database:
   CREATE DATABASE cyberpatriot_runbook;

3. Configure database connection in config.py or set DATABASE_URL environment variable

4. Run the application:
   python main.py

Features:
- User authentication with role-based access control (Member, Captain, Coach, Admin)
- Admin dashboard for team and user management
- Member dashboard for checklist completion and documentation
- README management for team knowledge base
- Encrypted note system for sensitive information
- Comprehensive activity logging and audit trails
- Team-based access controls

Architecture:
- PySide6 for responsive desktop GUI
- SQLAlchemy ORM with Alembic migrations
- MySQL database backend
- Modular controller-based architecture
- Security-focused design with encryption

The application supports local deployment and Raspberry Pi deployment.
"""

__version__ = "1.0.0"
__author__ = "CyberPatriot Team"

<div align="center">

# CyberPatriot Runbook

Desktop GUI application for managing CyberPatriot team checklists, documentation, and notes.

[![Docs](https://img.shields.io/badge/docs-website-blue)](https://michael6gledhill.github.io/cyberpatriot-runbook/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license)

</div>


Quick links:
- Project documentation: https://michael6gledhill.github.io/cyberpatriot-runbook/
- Getting started: docs/setup.md
- Usage guide: docs/usage.md

Overview
- Role‑based desktop application built with PySide6 (no web server)
- MySQL backend via SQLAlchemy ORM and Alembic migrations
- Secure authentication with bcrypt and encrypted sensitive notes
- Runs locally on Windows/macOS/Linux and deployable to Raspberry Pi

Features
- Authentication: login/signup with roles (member, captain, coach, admin)
- Admin Dashboard: team CRUD, pending user approvals, role changes, removals, activity log
- Team Member Dashboard: checklist hub, README manager, encrypted notes with sort/filter
- Team Join Requests: request to join teams, coach/admin approvals
- Audit Logging: visibility into important administrative actions

Requirements
- Python 3.10+
- MySQL 8.0+ (or MariaDB equivalent)
- See `requirements.txt` for Python dependencies

Install
```bash
pip install -r requirements.txt
```

Configure Database
- Create a database:
```sql
CREATE DATABASE cyberpatriot_runbook CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
- Set the connection string (preferred via environment variable):
```bash
set DATABASE_URL=mysql+pymysql://<user>:<password>@localhost:3306/cyberpatriot_runbook
```
Or edit `config.py` to provide `DATABASE_URL`.

Initialize Schema (Alembic)
```bash
alembic upgrade head
```

Run the App
```bash
python main.py
```

Raspberry Pi Notes
- Install the same `requirements.txt`
- Ensure MySQL is accessible (local or remote)
- Use the same `DATABASE_URL` and run `alembic upgrade head` before launching

Documentation
- Full documentation (with screenshots and guides) is published at:
  - https://michael6gledhill.github.io/cyberpatriot-runbook/
- To build locally with MkDocs:
```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

Contributing
- Fork and branch off `main`
- Use clear commit messages and keep changes scoped
- Open a pull request with a short summary and testing notes

License
This project is licensed under the MIT License. See LICENSE for details.

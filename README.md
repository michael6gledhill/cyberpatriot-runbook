# CyberPatriot Runbook App

Python desktop app (PySide6 + SQLite) to manage teams, users, checklists, notes, readmes, and forensic questions. Includes Quarto docs hosted on GitHub Pages.

## Quick Start (Windows cmd)

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

## Structure
- `app/`: PySide6 application
- `app/db.py`: SQLite schema + connection
- `app/auth.py`: Signup/login + approvals logic
- `app/models.py`: Data models + CRUD functions
- `app/ui/`: GUI widgets (Login, Signup, Dashboard)
- `docs/`: Quarto markdown docs
- `_quarto.yml`: Quarto config for GitHub Pages

## Notes
- First run creates `cyberpatriot.db` next to the app.
- Configure server/db settings in the Settings dialog (placeholder).

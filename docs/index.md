---

# CyberPatriot Runbook Documentation

Professional user and operator guide for the CyberPatriot Runbook desktop application.

This site covers installation, configuration, role-based workflows, and troubleshooting. The app is a PySide6 desktop client using MySQL with SQLAlchemy and Alembic.

> View the source on GitHub: https://github.com/michael6gledhill/cyberpatriot-runbook

## Quick Start
- Install Python dependencies: `pip install -r requirements.txt`
- Configure `DATABASE_URL` (MySQL): see Setup
- Initialize DB schema: `alembic upgrade head`
- Launch: `python main.py`

## What You’ll Find Here
- Overview: architecture, roles, and data flow
- Setup: environment, database, and migration steps
- Usage: login/sign-up, dashboards, approvals, and daily tasks
- Roles: capabilities for Admin, Coach, Captain, Member
- Teams: creation, join requests, and member lifecycle
- Dashboards: Admin/Coach/Member features
- Security: hashing, encryption, and best practices
- Troubleshooting: common issues and fixes

## Support & Contributions
- Open an issue or pull request on GitHub
- Follow conventional commits and include clear reproduction steps for bugs

## Local Docs Preview
```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

The documentation will be available at http://127.0.0.1:8000/ while serving.

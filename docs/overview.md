# Overview

CyberPatriot Runbook is a desktop application (PySide6) that helps teams manage roles, teams, join requests, checklists, notes, and audit logs for CyberPatriot competitions. It uses MySQL with SQLAlchemy, a repository layer, and role-aware dashboards for admins, coaches, captains, and members.

## Architecture
- **UI**: PySide6 (Qt) with dedicated dashboards per role
- **Backend**: SQLAlchemy ORM with repository layer
- **Database**: MySQL (schema in `database_setup.sql`)
- **Security**: bcrypt-based hashing, PBKDF2-HMAC encryption helpers
- **Roles**: `admin`, `coach`, `captain`, `member`

## Key Features
- Account creation with role selection and approval flow
- Team creation, join requests, and membership approvals
- Dashboards tailored to role capabilities
- Checklists, READMEs, notes, and audit logging
- MySQL-backed data persistence with repositories

## Data Flow
1. UI triggers repository calls (no direct session handling in UI).
2. Repositories open/close sessions and return ORM objects (with eager-loaded relationships).
3. GUI displays data and emits actions back to repositories/controllers.

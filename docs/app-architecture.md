# CyberPatriot Runbook — App Architecture (AI-Repro Prompt)

This page concisely documents the entire app so someone (or an AI) can recreate it from scratch. It prioritizes clarity and breadth while staying compact.

## Goals
- Desktop GUI for CyberPatriot team management: users, teams, approvals, checklists, READMEs, notes.
- MySQL backend with reliable migrations and a simple remote setup (Ubuntu Docker).
- Role-based dashboards: Admin, Coach, Captain, Competitor, Mentor.

## Tech Stack
- GUI: PySide6
- ORM: SQLAlchemy 2.x
- Migrations: Alembic
- DB Driver: PyMySQL
- Security: bcrypt (passwords), optional cryptography for note encryption
- Config: `.env` with `DATABASE_URL` or in-app Settings dialog

## Data Model (tables + relationships)
- `users`
  - id, name, email (unique), password_hash, role (`member|captain|coach|admin`), team_id (FK teams.id), is_approved, is_active, created_at, updated_at
  - relationships: `team` (many-to-one Team), `created_teams` (one-to-many Team), `join_requests`, `audit_logs`
- `teams`
  - id, name, team_id (NN-NNNN unique), division, created_by_user_id (FK users.id), created_at, updated_at
  - relationships: `members` (one-to-many User), `creator` (User), `readmes`, `notes`
- `checklists`, `checklist_items`, `checklist_status`
  - checklist_items belong to a checklist; checklist_status belongs to (user, checklist_item) with `status` and `notes`
- `readmes` (team docs): id, team_id, author_user_id, title, os_type, content
- `notes` (optionally encrypted): id, team_id, author_user_id, title, note_type, content
- `audit_logs`: id, user_id, action, resource_type, resource_id, description, created_at
- `team_join_requests`: id, team_id, requester_user_id, team_creator_user_id, status (`pending|approved|rejected`), message, created_at

## Repositories (service layer)
All CRUD and domain operations live in `app/database/repositories.py` using a global session factory (`app/database/__init__.py`). Key methods:
- `UserRepository`
  - `create_user(name, email, password_hash, team_id, role)` → auto-approve admins
  - `get_user_by_email`, `get_user_by_id`, `get_all_users`, `get_pending_users`
  - `approve_user(user_id)`, `reject_user(user_id)`, `delete_user(user_id)` (hard delete), `update_user_role(user_id, role)`
- `TeamRepository`
  - `create_team(name, team_id, division, created_by_user_id)` → if creator is coach, auto-assign them to the team and approve
  - `get_team_by_team_id`, `get_team_by_id`, `get_all_teams`, `get_teams_by_creator(creator_id)`, `update_team`, `delete_team`
- `ChecklistRepository` / `ReadMeRepository` / `NoteRepository`
  - CRUD for their respective resources and linking to teams/users
- `AuditLogRepository`
  - `log_action(user_id, action, resource_type, resource_id?, description?)`
- `TeamJoinRequestRepository`
  - `create_request(team_id, requester_user_id, team_creator_user_id, message)`
  - `approve_request(id)` (sets requester approved and attaches to team)
  - `reject_request(id)`
  - `get_pending_requests_for_creator(user_id)`, `get_pending_requests_for_team(team_id)`

## Configuration & DB Setup
- `.env` with `DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@SERVER_IP:3306/cyberpatriot_runbook`
- Alembic prefers environment variable; run `alembic upgrade head` after setting.
- Ubuntu backend via Docker Compose (see `backend-ubuntu.md`): single MySQL service with a persistent volume.

## GUI Structure
- `MainWindow` (QStackedWidget): switches between Login and role dashboards.
- `LoginWindow` (QMainWindow): tabs for Login, Sign Up, Documentation, and a Settings button.
  - Settings dialog (`app/gui/dialogs/settings_dialog.py`): Host/IP, Port, Username, Password, Database → builds `DATABASE_URL`, tests connection, writes `.env`, and reinitializes DB.
- Dashboards:
  - Admin: team management (create/edit/delete), user approvals, member management (approve/change role/delete), audit log.
  - Coach: my teams (create/join), team members, join requests, activity log. Creating a team auto-adds coach to the team.
  - Captain: checklists, READMEs, notes; team members (Approve/Reject competitors); join requests with pending count badge.
  - Member/Competitor: checklists, READMEs, notes; join requests.

## Key User Flows
- Signup:
  - Admin/Coach auto-login; others pending approval.
  - Captains must provide an existing Team ID (NN-NNNN).
- Approvals:
  - Admin can approve/reject/delete any user; sees team association.
  - Coach can approve team members and handle join requests to their teams.
  - Captain can approve competitors via Team Members and Join Requests.
- Team Creation:
  - Coach creating a team is auto-assigned (`user.team_id = team.id`) and approved.
- Settings:
  - From Login, configure backend DB and persist to `.env`. Connection test required for save.

## Security
- Passwords hashed with bcrypt; `PasswordManager.verify_password` on login.
- Optional encryption for notes via a symmetric key.
- Audit logging for admin actions: approve/reject/change role/delete.

## Minimal Files to Recreate
- Models: `app/models/user.py`, `team.py`, `checklist.py`, `readme.py`, `note.py`, `audit_log.py`, `team_join_request.py`
- DB init: `app/database/__init__.py`
- Repos: `app/database/repositories.py`
- GUI: `app/gui/login_window.py`, `main_window.py`, `admin_dashboard.py`, `coach_dashboard.py`, `member_dashboard.py`, `competitor_dashboard.py`, `mentor_dashboard.py`, `dialogs/settings_dialog.py`
- Entry: `main.py` (reads `DATABASE_URL`, calls `init_db`, launches `MainWindow`)
- Migrations: `alembic/` with `env.py` preferring env var and versions

## Build & Run
```bash
# Install
pip install -r requirements.txt

# Set DB and migrate
set DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@SERVER_IP:3306/cyberpatriot_runbook
alembic upgrade head

# Run
python main.py
```

## Prompt for AI Recreation
“Build a PySide6 desktop app ‘CyberPatriot Runbook’ with role-based dashboards (admin/coach/captain/member/competitor/mentor). Use SQLAlchemy 2.x with models and relationships as described, Alembic migrations, and PyMySQL. Implement repositories for Users, Teams, Checklists, READMEs, Notes, AuditLogs, JoinRequests with methods listed. Add a Login window with Sign Up, Settings (to configure `DATABASE_URL`, test connection, save to `.env`), and a Documentation tab. Implement Admin dashboard for team/user management with delete/change role and audit logging; Coach dashboard for team creation (auto-assign coach), members, join requests; Captain dashboard with members approval for competitors and join requests with a pending badge; Member/Competitor dashboards for checklists, READMEs, notes. Provide quick-start commands and make configuration via `.env`.”

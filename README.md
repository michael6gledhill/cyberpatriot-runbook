<div align="center">

# CyberPatriot Runbook

Desktop GUI application for managing CyberPatriot team checklists, documentation, and notes.

[![Docs](https://img.shields.io/badge/docs-website-blue)](https://michael6gledhill.github.io/cyberpatriot-runbook/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license)

</div>


Quick links:
- Project documentation: https://michael6gledhill.github.io/cyberpatriot-runbook/
- Backend on Ubuntu: docs/backend-ubuntu.md
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
- Create a database (Docker Compose on Ubuntu does this automatically):
```sql
CREATE DATABASE cyberpatriot_runbook CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
- Set the connection string (preferred via environment variable). Windows `cmd.exe` example:
```cmd
set DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@SERVER_IP:3306/cyberpatriot_runbook
```
Replace `SERVER_IP` with your Ubuntu server IP. For special characters in the password, escape `&` and `|` with `^`; avoid `!` in delayed expansion (use a fresh `cmd` or `cmd /v:off`).

Initialize Schema (Alembic)
```bash
alembic upgrade head
```

Run the App
```bash
python main.py
```

Backend on Ubuntu (Docker)
- Run MySQL via Docker Compose on Ubuntu Server
- Persist data via Docker volume; expose port 3306 to LAN

Quick start on Ubuntu Server:
```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release; echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
mkdir -p ~/cyberpatriot-backend && cd ~/cyberpatriot-backend
cat > docker-compose.yml << 'YML'
services:
  db:
    image: mysql:8.0
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: cyberpatriot_runbook
      MYSQL_USER: cp_user
      MYSQL_PASSWORD: your-strong-password
      MYSQL_ROOT_PASSWORD: your-strong-root-password
    ports:
      - "3306:3306"
    command: ["--character-set-server=utf8mb4", "--collation-server=utf8mb4_0900_ai_ci"]
    volumes:
      - db_data:/var/lib/mysql
volumes:
  db_data:
YML
docker compose up -d
```

Local frontend configuration (Windows `cmd.exe`):
```bat
set DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@<SERVER_IP>:3306/cyberpatriot_runbook
alembic upgrade head
python main.py
```

See `docs/backend-ubuntu.md` for the complete Ubuntu backend guide.

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

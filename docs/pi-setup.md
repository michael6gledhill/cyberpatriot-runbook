# Ubuntu Server Backend Setup (Docker)

This guide sets up the backend (MySQL) on an Ubuntu Server using Docker. The frontend (PySide6 desktop client) runs on your local computer(s) and connects to the Ubuntu-hosted database over the network.

> View the source on GitHub: https://github.com/michael6gledhill/cyberpatriot-runbook

## What Runs Where
- Ubuntu Server: MySQL server (database backend) via Docker Compose
- Local computers: CyberPatriot Runbook desktop app (frontend) and Alembic migrations

## Prerequisites
- Ubuntu Server with Docker and Docker Compose installed
- Internet connectivity and shell access
- Local computer(s) with Python installed to run the GUI

Install Docker & Compose:
```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# Log out/in to apply group membership
```
Compose v2 is bundled with recent Docker; if needed:
```bash
sudo apt install -y docker-compose-plugin
```

## 1. Start MySQL Backend with Docker
On the Ubuntu server, place `docker-compose.yml` in a directory, then run:

```bash
docker compose up -d
```

Environment defaults in `docker-compose.yml`:
- `MYSQL_DATABASE=cyberpatriot_runbook`
- `MYSQL_USER=cp_user`
- `MYSQL_PASSWORD=your-strong-password`
- `MYSQL_ROOT_PASSWORD=change-this-root-password`

To change credentials, edit `docker-compose.yml` and restart:
```bash
docker compose down
docker compose up -d
```

## 2. Run Alembic Migrations from a Local Computer
On your local computer (not on the Pi), clone the repository and configure the `DATABASE_URL` to point to the Pi.

```bash
git clone https://github.com/michael6gledhill/cyberpatriot-runbook.git
cd cyberpatriot-runbook
pip install -r requirements.txt
```

Set `DATABASE_URL` (replace `<PI_IP>`):

```bash
set DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@<SERVER_IP>:3306/cyberpatriot_runbook
```

Run migrations:

```bash
alembic upgrade head
```

## 3. Run the Frontend on Local Computers
On any local computer that will use the app:

```bash
git clone https://github.com/michael6gledhill/cyberpatriot-runbook.git
cd cyberpatriot-runbook
pip install -r requirements.txt
set DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@<SERVER_IP>:3306/cyberpatriot_runbook
python main.py
```

## 4. Optional: Configure `DATABASE_URL` on the Server for Admin Tasks
If you prefer to run Alembic from the Pi instead, set `DATABASE_URL` there:

```bash
echo 'DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@localhost:3306/cyberpatriot_runbook' | sudo tee -a /etc/environment
```
Log out/in or `source /etc/environment` to apply.

## 5. Network and Security Notes
- Restrict MySQL access to your LAN/subnets as needed.
- Consider firewall rules allowing TCP 3306 only from trusted hosts.
- Use strong passwords and rotate credentials periodically.

## 6. Verify Connectivity from Local Computers
From your local computer, test connectivity:

```bash
mysql -h <PI_IP> -u cp_user -p
```
If successful, the GUI will operate normally against the Pi-hosted database.

## 7. Docker Notes
- The compose file exposes `3306:3306` for MySQL access.
- Data is persisted in the `db_data` Docker volume.
- To stop/start:
```bash
docker compose down
docker compose up -d
```

## 8. Frontend Deployment Tips
- Distribute the desktop app by cloning the repo on each local machine.
- Configure `DATABASE_URL` to point to the Pi’s IP.
- Keep clients updated via `git pull` when you make changes.

## 9. Troubleshooting
- Access denied:
  - Verify `cp_user` credentials and privileges.
  - Test: `mysql -h localhost -u cp_user -p`
- Alembic/migration errors:
  - `alembic history`, `alembic current` to inspect.
  - `alembic downgrade -1` then `upgrade head` if needed.
- PySide6 display issues:
  - Run the app on a local desktop; the Pi should only host MySQL.

## 10. Next Steps
- On a local computer, run the desktop app and create an admin account.
- Configure teams and begin approvals; data persists on the Pi MySQL.

## Documentation
- Full project documentation: https://michael6gledhill.github.io/cyberpatriot-runbook/
- View the source on GitHub: https://github.com/michael6gledhill/cyberpatriot-runbook
- Local docs preview:
```bash
sudo pip3 install mkdocs mkdocs-material
mkdocs serve
```
Open http://127.0.0.1:8000/ in your browser.

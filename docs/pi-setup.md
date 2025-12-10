# Raspberry Pi (CasaOS) Backend Setup

This guide walks through installing and configuring the CyberPatriot Runbook backend on a Raspberry Pi running CasaOS. These steps avoid Python virtual environments and install system-wide packages.

> View the source on GitHub: https://github.com/michael6gledhill/cyberpatriot-runbook

## Prerequisites
- Raspberry Pi (64-bit OS recommended) with CasaOS installed
- MySQL server installed and running (local or remote)
- A MySQL user/password and the database name you will use (e.g., `cyberpatriot_runbook`)
- Internet connectivity and basic shell access

## 1. Update System and Install Dependencies
Update APT and install required packages and Python dependencies:

```bash
sudo apt update
sudo apt install -y python3 python3-pip git build-essential libssl-dev libffi-dev
```

Notes:
- `python3-pip` installs pip system-wide (no virtualenv used).
- `build-essential` and OpenSSL/ffi headers help compile dependencies if needed.

## 2. Get the Application Source Code
Clone the repository to your Pi:

```bash
cd ~
git clone https://github.com/michael6gledhill/cyberpatriot-runbook.git
cd cyberpatriot-runbook
```

To update later:
```bash
git pull
```

## 3. Install Python Requirements (System-wide)
Install dependencies listed in `requirements.txt`:

```bash
sudo pip3 install --upgrade pip
sudo pip3 install -r requirements.txt
```

Packages installed:
- PySide6 (GUI)
- SQLAlchemy
- PyMySQL
- bcrypt
- cryptography
- Alembic
- python-dotenv

## 4. Prepare MySQL Database
Log in to MySQL and create the database and a dedicated user. If you already have these, you can skip this step.

```bash
mysql -u root -p
```
Inside MySQL shell:
```sql
CREATE DATABASE cyberpatriot_runbook CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'cp_user'@'localhost' IDENTIFIED BY 'your-strong-password';
GRANT ALL PRIVILEGES ON cyberpatriot_runbook.* TO 'cp_user'@'localhost';
FLUSH PRIVILEGES;
```

If you plan to connect from another machine, grant to `%` and ensure MySQL listens on all interfaces:
```sql
CREATE USER 'cp_user'@'%' IDENTIFIED BY 'your-strong-password';
GRANT ALL PRIVILEGES ON cyberpatriot_runbook.* TO 'cp_user'@'%';
FLUSH PRIVILEGES;
```

## 5. Configure the Database URL
The application reads the database connection from `DATABASE_URL`. Set it in your shell or add it to `/etc/environment` for persistence.

Example for local MySQL:
```bash
export DATABASE_URL="mysql+pymysql://cp_user:your-strong-password@localhost:3306/cyberpatriot_runbook"
```

To persist across reboots, add the line to `/etc/environment`:
```bash
echo 'DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@localhost:3306/cyberpatriot_runbook' | sudo tee -a /etc/environment
```
Log out/in or `source /etc/environment` to apply.

Alternatively, you can edit `config.py` and set `DATABASE_URL` directly.

## 6. Initialize the Database Schema (Alembic)
Run Alembic migrations to create the tables:

```bash
alembic upgrade head
```

This will create the following tables and relationships:
- users, teams, team_join_requests
- checklists, checklist_items, checklist_status
- readmes, notes (with encryption support)
- audit_logs

## 7. Run the Application (GUI)
Launch the desktop application from the repository directory:

```bash
python3 main.py
```

You should see output similar to:
```
Initializing database: mysql+pymysql://cp_user:***@localhost:3306/cyberpatriot_runbook
Database initialized successfully!
```
The PySide6 window should open if you’re running in a graphical session on the Pi.

## 8. Remote Database Access (Optional)
If you will run the GUI on another machine but use the Pi’s MySQL:
- Ensure MySQL listens on `0.0.0.0`:
  - Edit `/etc/mysql/mysql.conf.d/mysqld.cnf`, set `bind-address = 0.0.0.0`
  - Restart: `sudo systemctl restart mysql`
- Open/allow TCP 3306 in CasaOS/iptables or restrict to your LAN.
- Set `DATABASE_URL` on your desktop to point to the Pi IP:
```bash
export DATABASE_URL="mysql+pymysql://cp_user:your-strong-password@<PI_IP>:3306/cyberpatriot_runbook"
```

## 9. CasaOS Considerations
- CasaOS often manages services via containers; here we run the app directly on the host.
- Use system packages and environment variables as shown; avoid virtualenvs per your requirement.
- If you containerize later, reuse the same `DATABASE_URL` and run `alembic upgrade head` in the container.

## 10. Troubleshooting
- Access denied:
  - Verify `cp_user` credentials and privileges.
  - Test: `mysql -h localhost -u cp_user -p`
- Alembic/migration errors:
  - `alembic history`, `alembic current` to inspect.
  - `alembic downgrade -1` then `upgrade head` if needed.
- PySide6 display issues:
  - Ensure you’re in a graphical session (not headless).
  - On headless, use X forwarding or run the app on a desktop pointing to Pi DB.

## 11. Next Steps
- Create an admin account and log in to the Admin Dashboard.
- Create teams, approve join requests (admins/coaches), and start using checklists, READMEs, and notes.

## Documentation
- Full project documentation: https://michael6gledhill.github.io/cyberpatriot-runbook/
- View the source on GitHub: https://github.com/michael6gledhill/cyberpatriot-runbook
- Local docs preview:
```bash
sudo pip3 install mkdocs mkdocs-material
mkdocs serve
```
Open http://127.0.0.1:8000/ in your browser.

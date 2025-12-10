# Raspberry Pi (CasaOS) Backend Setup

This guide focuses on running only the backend (MySQL database) on a Raspberry Pi running CasaOS. The application frontend (PySide6 desktop client) runs on your local computer(s) and connects to the Pi-hosted database over the network.

> View the source on GitHub: https://github.com/michael6gledhill/cyberpatriot-runbook

## What Runs Where
- Raspberry Pi: MySQL server (database backend)
- Local computers: CyberPatriot Runbook desktop app (frontend) and Alembic migrations

## Prerequisites
- Raspberry Pi (64-bit OS recommended) with CasaOS installed
- Internet connectivity and shell access
- Local computer(s) with Python installed to run the GUI

## 1. Install and Configure MySQL on the Pi
Update APT and install MySQL server:

```bash
sudo apt update
sudo apt install -y mysql-server
```

Secure and start MySQL:

```bash
sudo systemctl enable mysql
sudo systemctl start mysql
sudo mysql_secure_installation
```

## 2. Create Database and User on the Pi
Log in to MySQL and create the database and a dedicated user.

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

If you plan to connect from other machines, grant to `%` and ensure MySQL listens on all interfaces:
```sql
CREATE USER 'cp_user'@'%' IDENTIFIED BY 'your-strong-password';
GRANT ALL PRIVILEGES ON cyberpatriot_runbook.* TO 'cp_user'@'%';
FLUSH PRIVILEGES;
```

Enable remote connections:
- Edit `/etc/mysql/mysql.conf.d/mysqld.cnf` and set `bind-address = 0.0.0.0`
- Restart MySQL: `sudo systemctl restart mysql`

## 3. Run Alembic Migrations from a Local Computer
On your local computer (not on the Pi), clone the repository and configure the `DATABASE_URL` to point to the Pi.

```bash
git clone https://github.com/michael6gledhill/cyberpatriot-runbook.git
cd cyberpatriot-runbook
pip install -r requirements.txt
```

Set `DATABASE_URL` (replace `<PI_IP>`):

```bash
set DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@<PI_IP>:3306/cyberpatriot_runbook
```

Run migrations:

```bash
alembic upgrade head
```

## 4. Run the Frontend on Local Computers
On any local computer that will use the app:

```bash
git clone https://github.com/michael6gledhill/cyberpatriot-runbook.git
cd cyberpatriot-runbook
pip install -r requirements.txt
set DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@<PI_IP>:3306/cyberpatriot_runbook
python main.py
```

## 5. Optional: Configure `DATABASE_URL` on the Pi for Admin Tasks
If you prefer to run Alembic from the Pi instead, set `DATABASE_URL` there:

```bash
echo 'DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@localhost:3306/cyberpatriot_runbook' | sudo tee -a /etc/environment
```
Log out/in or `source /etc/environment` to apply.

## 6. Network and Security Notes
- Restrict MySQL access to your LAN/subnets as needed.
- Consider firewall rules allowing TCP 3306 only from trusted hosts.
- Use strong passwords and rotate credentials periodically.

## 7. Verify Connectivity from Local Computers
From your local computer, test connectivity:

```bash
mysql -h <PI_IP> -u cp_user -p
```
If successful, the GUI will operate normally against the Pi-hosted database.

## 8. CasaOS Considerations
- CasaOS may manage services via containers; this guide uses host-installed MySQL.
- For containerization later, expose port 3306 and use the same `DATABASE_URL`.

## 9. Frontend Deployment Tips
- Distribute the desktop app by cloning the repo on each local machine.
- Configure `DATABASE_URL` to point to the Pi’s IP.
- Keep clients updated via `git pull` when you make changes.

## 10. Troubleshooting
- Access denied:
  - Verify `cp_user` credentials and privileges.
  - Test: `mysql -h localhost -u cp_user -p`
- Alembic/migration errors:
  - `alembic history`, `alembic current` to inspect.
  - `alembic downgrade -1` then `upgrade head` if needed.
- PySide6 display issues:
  - Run the app on a local desktop; the Pi should only host MySQL.

## 11. Next Steps
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

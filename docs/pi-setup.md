# Ubuntu Server Backend Setup (Docker)

This guide sets up the backend database on Ubuntu Server in the simplest, safest way possible. You don’t need prior experience. Just follow the steps exactly and copy the commands.

What we’ll do:
- Install Docker (a safe app runner)
- Start the database with one command
- Point your computer’s app to that server

> View the source on GitHub: https://github.com/michael6gledhill/cyberpatriot-runbook

## What Runs Where
- Ubuntu Server: MySQL server (database backend) via Docker Compose
- Local computers: CyberPatriot Runbook desktop app (frontend) and Alembic migrations

## Prerequisites
- An Ubuntu Server (connected to the internet)
- A local computer that will run the app (Windows/macOS/Linux)

If you are on a home/school network, use a wired connection for the server if possible. Write down the server’s IP address (you can find it with `ip a` or ask your network admin).

## Step 1: Install Docker
Run these commands on the Ubuntu Server. Copy and paste exactly.

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

Now log out and log back in (this activates permissions). If you use SSH, close the window and reconnect.

Optional: If `docker compose` is not found, install the plugin:
```bash
sudo apt install -y docker-compose-plugin
```

## Step 2: Start the Database (MySQL)
On the Ubuntu Server, go to the folder where the file `docker-compose.yml` is located (the project root). If you don’t have it on the server yet, you can copy it from your computer or clone the repository.

Start the database:

```bash
docker compose up -d
```

This starts MySQL and saves data so it is not lost when the server restarts.

Important passwords (you can change them later by editing `docker-compose.yml`):
- `MYSQL_DATABASE=cyberpatriot_runbook` (database name)
- `MYSQL_USER=cp_user` (username for the app)
- `MYSQL_PASSWORD=your-strong-password` (change this to your own)
- `MYSQL_ROOT_PASSWORD=change-this-root-password` (admin password for MySQL)

To change credentials, edit `docker-compose.yml` and restart:
```bash
docker compose down
docker compose up -d
```

## Step 3: Prepare the Database (from your computer)
On your local computer, we will create the tables. Do this once.

1) Download the app code:

```bash
git clone https://github.com/michael6gledhill/cyberpatriot-runbook.git
cd cyberpatriot-runbook
pip install -r requirements.txt
```

2) Set the connection to the server database (replace `<SERVER_IP>` with your server’s IP address):

```bash
set DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@<SERVER_IP>:3306/cyberpatriot_runbook
```

3) Create the tables:

```bash
alembic upgrade head
```

## Step 4: Run the App (on your computer)
Any computer can run the app. Repeat these steps on each computer that needs it.

```bash
git clone https://github.com/michael6gledhill/cyberpatriot-runbook.git
cd cyberpatriot-runbook
pip install -r requirements.txt
set DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@<SERVER_IP>:3306/cyberpatriot_runbook
python main.py
```

## Optional: Server-only Admin Tasks
If you prefer to run the database setup from the server itself, set `DATABASE_URL` on the server:

```bash
echo 'DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@localhost:3306/cyberpatriot_runbook' | sudo tee -a /etc/environment
```
Log out/in or `source /etc/environment` to apply.

## Safety and Network Tips
- Restrict MySQL access to your LAN/subnets as needed.
- Consider firewall rules allowing TCP 3306 only from trusted hosts.
- Use strong passwords and rotate credentials periodically.
- Keep your `MYSQL_ROOT_PASSWORD` private.
- Don’t share the `DATABASE_URL` publicly.

## Check: Can your computer reach the server?
From your local computer, test connectivity:

```bash
mysql -h <PI_IP> -u cp_user -p
```
If successful, the app will work against the Ubuntu-hosted database.

## Docker Notes
- The compose file exposes `3306:3306` for MySQL access.
- Data is persisted in the `db_data` Docker volume.
- To stop/start:
```bash
docker compose down
docker compose up -d
```

## Frontend Tips
- Distribute the desktop app by cloning the repo on each local machine.
- Configure `DATABASE_URL` to point to the Pi’s IP.
- Keep clients updated via `git pull` when you make changes.

## Troubleshooting
- Access denied:
  - Verify `cp_user` credentials and privileges.
    - Test: `mysql -h <SERVER_IP> -u cp_user -p`
- Alembic/migration errors:
  - `alembic history`, `alembic current` to inspect.
  - `alembic downgrade -1` then `upgrade head` if needed.
- PySide6 display issues:
  - Run the app on a local desktop; the Pi should only host MySQL.

## Next Steps
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

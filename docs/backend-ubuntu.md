# Ubuntu Server Backend (Docker)

This guide gets your backend running on Ubuntu Server using Docker in minutes, then connects your Windows/macOS desktop app to it.

## 1) Install Docker Engine

```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release; echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

Verify Docker:
```bash
docker version
```

## 2) Start MySQL with Docker Compose

```bash
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

Note your server IP:
```bash
hostname -I
```

## 3) Windows/macOS client setup

Clone and install dependencies:
```cmd
git clone https://github.com/michael6gledhill/cyberpatriot-runbook.git
cd cyberpatriot-runbook
pip install -r requirements.txt
```

Set your `DATABASE_URL` (Windows cmd):
```cmd
set DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@SERVER_IP:3306/cyberpatriot_runbook
```
- Replace `SERVER_IP` with your Ubuntu server IP.
- Escaping: use `^` before `&` or `|` if present in the password; avoid `!` with delayed expansion.

Initialize the schema:
```cmd
alembic upgrade head
```

Run the app:
```cmd
python main.py
```

## 4) Optional: persist config via .env
Create a `.env` file in the repo root:
```
DATABASE_URL=mysql+pymysql://cp_user:your-strong-password@SERVER_IP:3306/cyberpatriot_runbook
```
The app and Alembic will use this automatically when `DATABASE_URL` is not set in the environment.

## 5) Firewall & connectivity
- Ensure port `3306` is reachable on your LAN.
- If using UFW:
```bash
sudo ufw allow 3306/tcp
sudo ufw status
```
- Confirm from Windows:
```powershell
Test-NetConnection -ComputerName SERVER_IP -Port 3306
```

## Troubleshooting
- Authentication fails or approvals error: update to latest app and run `alembic upgrade head` to apply migrations.
- Alembic complains about URL: ensure `DATABASE_URL` is set in current shell or `.env` exists.
- Connection refused: check `docker compose ps` and MySQL logs with `docker compose logs -f db`.
- Password special characters: prefer `.env` to avoid cmd escaping issues.

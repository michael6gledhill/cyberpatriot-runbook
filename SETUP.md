# CyberPatriot Runbook - Development Setup

This guide will help you set up the CyberPatriot Runbook application for development.

## System Requirements

- Python 3.9 or higher
- MySQL 5.7+ or MariaDB 10.3+
- Git
- 2GB RAM minimum
- Windows 10+, macOS 10.12+, Ubuntu 18.04+, or Raspberry Pi OS

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/michael6gledhill/cyberpatriot-runbook.git
cd cyberpatriot-runbook
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Database

#### Option A: Using MySQL CLI

```bash
mysql -u root -p < database_setup.sql
```

#### Option B: Using Python script

```python
python -c "from app.database import init_db; init_db()"
```

### 5. Configure Environment

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/cyberpatriot_runbook
```

### 6. Run the Application

```bash
python main.py
```

## Docker Setup (Optional)

```bash
# Build Docker image
docker build -t cyberpatriot-runbook .

# Run with Docker Compose
docker-compose up
```

## Raspberry Pi Deployment

### 1. Install Python and Dependencies

```bash
sudo apt-get update
sudo apt-get install python3.9 python3-pip python3-venv
sudo apt-get install default-mysql-server
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv /home/pi/cyberpatriot-runbook/venv
source /home/pi/cyberpatriot-runbook/venv/bin/activate
```

### 3. Install Project Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run as Service

Create `/etc/systemd/system/cyberpatriot-runbook.service`:

```ini
[Unit]
Description=CyberPatriot Runbook Application
After=network.target mysql.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/cyberpatriot-runbook
Environment="PATH=/home/pi/cyberpatriot-runbook/venv/bin"
ExecStart=/home/pi/cyberpatriot-runbook/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable cyberpatriot-runbook
sudo systemctl start cyberpatriot-runbook
```

## Usage

### Initial Admin Setup

1. Create initial admin user directly in database:

```sql
INSERT INTO users (name, email, password_hash, role, is_approved, is_active)
VALUES ('Admin User', 'admin@example.com', 'hashed_password_here', 'admin', TRUE, TRUE);
```

Or use the signup flow and modify the role to 'admin'.

### Adding Teams

1. Log in as admin
2. Go to Team Management tab
3. Click "Create Team"
4. Enter team name, team ID (format: NN-NNNN), and division

### Approving Users

1. Log in as admin
2. Go to User Approvals tab
3. Review pending users
4. Click Approve or Reject

### Creating Checklists

Insert sample checklists into the database:

```sql
INSERT INTO checklists (title, description, category)
VALUES 
  ('Ubuntu Server Security Hardening', 'Security checklist for Ubuntu 20.04', 'Ubuntu'),
  ('Windows 10 Security Config', 'Security checklist for Windows 10', 'Windows'),
  ('Cisco Router Config', 'Security checklist for Cisco routers', 'Cisco');
```

## Troubleshooting

### Database Connection Error

- Verify MySQL is running
- Check DATABASE_URL in .env
- Ensure database exists: `SHOW DATABASES;`

### PySide6 Installation Issues

On Linux, you may need:
```bash
sudo apt-get install libgl1-mesa-glx libxkbcommon-x11-0
```

### Raspberry Pi Display Issues

If using headless, use X11 forwarding or VNC:
```bash
DISPLAY=:0 python main.py
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
black app/
flake8 app/
```

### Database Migrations

```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup guide.

## License

See LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub.

# CyberPatriot Runbook - Getting Started Guide

## ⚡ 5-Minute Quick Start

### Prerequisites
- Python 3.9 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

### Step 1: Install Dependencies (2 minutes)
```bash
cd c:\Users\cadet\Documents\GitHub\cyberpatriot-runbook
pip install -r requirements.txt
```

### Step 2: Verify Setup (1 minute)
```bash
python setup_complete.py
```

### Step 3: Initialize Database (1 minute)
```bash
python init_database.py
```

### Step 4: Run Application (1 minute)
```bash
python main.py
```

**Login with:**
- Email: `admin@cyberpatriot.local`
- Password: `Admin@123`

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'PySide6'"

**Solution:**
```bash
pip install PySide6==6.6.1
pip install -r requirements.txt
```

### Issue: "Can't connect to MySQL server"

**Solution:**
1. Ensure MySQL is running:
   ```bash
   # Windows
   sc query MySQL80
   # If not running, start it
   net start MySQL80
   ```

2. Create database user:
   ```bash
   mysql -u root -p < database_setup.sql
   ```

3. Verify connection:
   ```bash
   mysql -u app -p1L!k3my9@55w0rd -h localhost cyberpatriot_runbook -e "SELECT 1;"
   ```

### Issue: "Database 'cyberpatriot_runbook' doesn't exist"

**Solution:**
```bash
# Run the database setup script
mysql -u root -p < database_setup.sql
# Then initialize database
python init_database.py
```

### Issue: "AttributeError: module has no attribute"

**Solution:**
1. Delete Python cache:
   ```bash
   rmdir /s /q app\__pycache__
   rmdir /s /q app\models\__pycache__
   rmdir /s /q app\database\__pycache__
   ```

2. Reinstall dependencies:
   ```bash
   pip install --upgrade --force-reinstall -r requirements.txt
   ```

### Issue: Application starts but GUI is blank

**Solution:**
1. Check Qt platform plugin:
   ```bash
   set QT_DEBUG_PLUGINS=1
   python main.py
   ```

2. Reinstall PySide6:
   ```bash
   pip uninstall PySide6 -y
   pip install PySide6==6.6.1
   ```

### Issue: "Port 3306 already in use"

**Solution:**
```bash
# Find process using port 3306
netstat -ano | findstr 3306
# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
# Then restart MySQL
net start MySQL80
```

---

## 📋 Complete Setup Instructions

### 1. Prepare Your System

#### Install Python 3.9+
- Download from https://www.python.org/downloads/
- During installation, **CHECK** "Add Python to PATH"
- Verify installation:
  ```bash
  python --version
  ```

#### Install MySQL 5.7+
- Download from https://dev.mysql.com/downloads/mysql/
- During installation, note your root password
- Start MySQL service:
  ```bash
  net start MySQL80
  ```

### 2. Clone/Access Repository
```bash
cd c:\Users\cadet\Documents\GitHub\cyberpatriot-runbook
```

### 3. Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

Expected output should show all packages installing successfully:
- PySide6 6.6.1
- SQLAlchemy 2.0.23
- PyMySQL 1.1.0
- alembic 1.13.1
- bcrypt 4.1.1
- cryptography 41.0.7

### 5. Configure Database

#### Option A: Using SQL Script
```bash
# From MySQL command line
mysql -u root -p
# Enter your MySQL root password
# Paste contents of database_setup.sql
```

#### Option B: Using Command Line
```bash
mysql -u root -p < database_setup.sql
```

### 6. Initialize Database with Sample Data
```bash
python init_database.py
```

This will:
- Create all tables
- Create sample team (Blue Squadron)
- Create admin user
- Log initialization

### 7. Configure Application

Create `.env` file in project root:
```bash
# Copy from example
copy .env.example .env

# Edit .env with your settings
# Windows:
# DATABASE_URL=mysql+pymysql://app:1L!k3my9@55w0rd@localhost:3306/cyberpatriot_runbook
# APP_DEBUG=False
# APP_LOG_LEVEL=INFO
```

### 8. Verify Setup
```bash
python setup_complete.py
```

You should see all checks pass with ✅ marks.

### 9. Run Application
```bash
python main.py
```

The application window should open with login screen.

---

## 🔐 First-Time Setup Checklist

- [ ] Python 3.9+ installed
- [ ] MySQL 5.7+ installed and running
- [ ] Repository cloned/accessed
- [ ] Virtual environment created (optional)
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Database created: `mysql -u root -p < database_setup.sql`
- [ ] Database initialized: `python init_database.py`
- [ ] Setup verified: `python setup_complete.py` (all ✅)
- [ ] `.env` file configured
- [ ] Application starts: `python main.py`
- [ ] Can login with admin@cyberpatriot.local / Admin@123

---

## 👥 Default User Accounts

### Admin Account (Created during init_database.py)
- **Email:** admin@cyberpatriot.local
- **Password:** Admin@123
- **Role:** Admin
- **Team:** Blue Squadron (01-0001)

**⚠️ Important:** Change this password immediately after first login!

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **START_HERE.md** | Project overview and features |
| **QUICKSTART.md** | 5-minute quick start (this file) |
| **SETUP.md** | Detailed setup instructions |
| **ARCHITECTURE.md** | Technical architecture |
| **TESTING.md** | Testing procedures |
| **FILE_INDEX.md** | File structure |
| **PROJECTREADME.md** | Professional README |

---

## 🎯 Common Tasks

### Change Admin Password
1. Login with default credentials
2. Go to Settings (if available)
3. Change password to something secure
4. Logout and login with new password

### Create New Team
1. Login as Admin
2. Go to Admin Dashboard
3. Click "Add Team"
4. Fill in team details
5. Click Create

### Add Team Member
1. Member signs up with team ID
2. Appears as "Pending" in Admin Dashboard
3. Admin approves the member
4. Member can now login

### Reset Admin User
```bash
# This will delete all data and recreate sample data
rm database_setup.sql
python init_database.py
```

---

## 🐛 Debug Mode

### Enable Debug Logging
Edit `config.py`:
```python
DEBUG = True
LOG_LEVEL = "DEBUG"
```

Then run:
```bash
python main.py
```

### View Application Logs
Logs are saved in the application directory (if configured).

### Check Database Directly
```bash
mysql -u app -p1L!k3my9@55w0rd cyberpatriot_runbook
# Then query tables:
# SELECT * FROM users;
# SELECT * FROM teams;
# SELECT * FROM audit_logs;
```

---

## 🚀 Advanced Setup

### Docker Deployment
```bash
docker-compose up
```

### Raspberry Pi Deployment
See SETUP.md for systemd service configuration.

### Production Deployment
See SETUP.md for production checklist.

---

## ✅ Verification Commands

```bash
# Check Python version
python --version

# Check pip packages
pip list | findstr /E "PySide6|SQLAlchemy|PyMySQL|alembic|bcrypt|cryptography"

# Check MySQL connection
mysql -u app -p1L!k3my9@55w0rd -h localhost cyberpatriot_runbook -e "SELECT VERSION();"

# Check project files
dir app
dir app\models
dir app\database
dir app\controllers
dir app\gui

# Verify setup
python setup_complete.py

# Initialize database
python init_database.py
```

---

## 🆘 Getting Help

### Check Logs
1. Application logs: Check application directory for `debug.log`
2. Database logs: Check MySQL log files
3. Setup logs: Check `setup_log.json` after running setup_complete.py

### Verify Installation
```bash
python -c "import PySide6; print('PySide6 OK')"
python -c "import sqlalchemy; print('SQLAlchemy OK')"
python -c "import pymysql; print('PyMySQL OK')"
python -c "import bcrypt; print('bcrypt OK')"
```

### Database Test
```bash
python init_database.py
```

### Full Diagnostic
```bash
python setup_complete.py
```

---

## 📞 Support Resources

- **PySide6:** https://doc.qt.io/qtforpython/
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **MySQL:** https://dev.mysql.com/doc/
- **Alembic:** https://alembic.sqlalchemy.org/
- **bcrypt:** https://github.com/pyca/bcrypt

---

## 🎉 Success!

Once you see the login screen, the application is working correctly!

**Next steps:**
1. Login with default admin account
2. Create your first team
3. Add team members
4. Start managing checklists

Enjoy your CyberPatriot Runbook application! 🚀

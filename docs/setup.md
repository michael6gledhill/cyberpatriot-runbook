# Setup

## Prerequisites
- Python 3.13
- MySQL server
- pip and virtualenv (recommended)

## Install
```bash
pip install -r requirements.txt
```

## Database
1. Create database `cyberpatriot_runbook` in MySQL.
2. Update credentials in `config.py` if needed (default root/h0gBog89!).
3. Initialize schema:
```bash
python init_database.py
```

## Run App
```bash
python main.py
```

## Environment
- GUI: PySide6
- ORM: SQLAlchemy 2.x
- Encryption: bcrypt + PBKDF2-HMAC

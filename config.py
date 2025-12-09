# CyberPatriot Runbook - Configuration

# Database Settings
# MySQL production configuration
DATABASE_URL = "mysql+pymysql://root:h0gBog89!@localhost:3306/cyberpatriot_runbook"

# For SQLite development/testing, use:
# DATABASE_URL = "sqlite:///cyberpatriot_runbook.db"

# Application Settings
APP_NAME = "CyberPatriot Runbook"
APP_VERSION = "1.0.0"

# Security Settings
PASSWORD_HASH_ROUNDS = 12
ENCRYPTION_ITERATIONS = 100000

# UI Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

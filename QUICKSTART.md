# CyberPatriot Runbook - Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Python 3.9+
- MySQL 5.7+ (local or remote)
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/michael6gledhill/cyberpatriot-runbook.git
cd cyberpatriot-runbook
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Database
```bash
# Create database
mysql -u root -p < database_setup.sql

# Or manually create:
# CREATE DATABASE cyberpatriot_runbook;
```

### Step 5: Configure
Edit `config.py` or set environment variable:
```bash
# Set DATABASE_URL
export DATABASE_URL=mysql+pymysql://root:password@localhost:3306/cyberpatriot_runbook
```

### Step 6: Run Application
```bash
python main.py
```

## First-Time Admin Setup

1. **Create Admin Account**:
   - Run the app and it will auto-initialize the database
   - Manually insert admin user in MySQL:
   ```sql
   USE cyberpatriot_runbook;
   INSERT INTO users (name, email, password_hash, role, is_approved, is_active)
   VALUES ('Admin', 'admin@example.com', '$2b$12$...', 'admin', TRUE, TRUE);
   ```

2. **Generate Password Hash** (in Python):
   ```python
   from app.security import PasswordManager
   hash = PasswordManager.hash_password("your_password")
   print(hash)
   ```

3. **Create Sample Team**:
   ```sql
   INSERT INTO teams (name, team_id, division)
   VALUES ('Team Alpha', '01-0001', 'Division B');
   ```

4. **Login** with admin credentials

## User Workflows

### Admin Workflow
1. Login with admin account
2. Go to "Team Management" → Create teams
3. Go to "User Approvals" → Approve pending signups
4. Go to "Member Management" → Manage roles
5. View "Activity Log" for audit trail

### Team Member Workflow
1. Sign up with team ID (NN-NNNN)
2. Wait for admin approval
3. Login to access:
   - **Checklists**: Mark items as pending/completed/skipped
   - **READMEs**: Create and share OS-specific documentation
   - **Notes**: Create secure encrypted notes

## Troubleshooting

### Database Connection Failed
```bash
# Check MySQL is running
mysql -u root -p -e "SELECT 1;"

# Verify DATABASE_URL
echo $DATABASE_URL

# Update config.py with correct credentials
```

### PySide6 Import Error
```bash
pip install --upgrade PySide6
```

### Permission Denied on Linux
```bash
chmod +x main.py
python main.py
```

## Key Features at a Glance

| Feature | Available | Location |
|---------|-----------|----------|
| User Authentication | ✓ | Login Tab |
| Team Management | ✓ | Admin Dashboard |
| User Approval System | ✓ | Admin Dashboard |
| Checklists | ✓ | Member Dashboard |
| READMEs | ✓ | Member Dashboard |
| Encrypted Notes | ✓ | Member Dashboard |
| Audit Logs | ✓ | Admin Dashboard |
| Role-Based Access | ✓ | Automatic |

## Configuration Options

Create `.env` file:
```env
DATABASE_URL=mysql+pymysql://root:password@localhost/cyberpatriot_runbook
DEBUG=False
LOG_LEVEL=INFO
```

## Default Roles

- **Admin**: Full system access, team management, user approval
- **Captain**: View team data, approve new members
- **Coach**: View team data, limited editing
- **Member**: Basic access, personal checklist tracking

## Database Reset

⚠️ **Warning**: This deletes all data!

```bash
mysql -u root -p cyberpatriot_runbook < /dev/null
mysql -u root -p < database_setup.sql
```

## Next Steps

1. Read [SETUP.md](SETUP.md) for detailed setup
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
3. Check [README.md](README.md) for features overview
4. Deploy to Raspberry Pi using [SETUP.md](SETUP.md)

## Common Commands

```bash
# Run application
python main.py

# Check database
mysql -u root -p cyberpatriot_runbook -e "SHOW TABLES;"

# View audit logs
mysql -u root -p cyberpatriot_runbook -e "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 10;"

# Backup database
mysqldump -u root -p cyberpatriot_runbook > backup.sql

# Restore database
mysql -u root -p cyberpatriot_runbook < backup.sql
```

## Support

For issues:
1. Check [SETUP.md](SETUP.md) troubleshooting
2. Review application logs
3. Open GitHub issue with error details

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready

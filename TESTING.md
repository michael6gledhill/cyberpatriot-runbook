# CyberPatriot Runbook - Testing & Validation Guide

## Pre-Deployment Validation Checklist

### Environment Setup ✓
- [ ] Python 3.9+ installed
- [ ] MySQL 5.7+ installed and running
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Database created: `mysql -u root -p < database_setup.sql`
- [ ] DATABASE_URL environment variable set correctly

### Database Validation

```bash
# Connect to MySQL
mysql -u root -p cyberpatriot_runbook

# Verify all tables exist
SHOW TABLES;

# Check table structure
DESCRIBE users;
DESCRIBE teams;
DESCRIBE checklists;
DESCRIBE checklist_items;
DESCRIBE checklist_status;
DESCRIBE readmes;
DESCRIBE notes;
DESCRIBE audit_logs;

# Verify foreign keys
SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME 
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = 'cyberpatriot_runbook' AND REFERENCED_TABLE_NAME IS NOT NULL;

# Exit
EXIT;
```

### Application Startup Test

```bash
# Start the application
python main.py

# Expected output:
# - No errors in console
# - Window opens with login screen
# - Can interact with UI
```

## Feature Testing Scenarios

### 1. User Authentication

#### Test 1.1: Admin Login
```
Scenario: Admin user logs in successfully
Steps:
1. Start application → Login tab
2. Insert admin credentials directly in DB:
   INSERT INTO users (name, email, password_hash, role, is_approved, is_active)
   VALUES ('Admin Test', 'admin@test.com', 
           '$2b$12$...hashed_password...', 'admin', TRUE, TRUE);
3. Generate hash: PasswordManager.hash_password('password123')
4. Enter email and password in login form
5. Click Login
Expected: Admin Dashboard opens

Validation:
✓ Admin Dashboard window opens
✓ Title shows admin name
✓ All tabs visible (Team Management, User Approvals, etc.)
```

#### Test 1.2: Member Signup
```
Scenario: New member signs up and awaits approval
Steps:
1. Click Sign Up tab
2. Enter:
   - Name: "Test Member"
   - Email: "member@test.com"
   - Password: "SecurePass123"
   - Confirm: "SecurePass123"
   - Role: Member
   - Team ID: "01-0001" (must exist in database)
3. Click Sign Up
Expected: Success message, account pending approval

Validation:
✓ Success dialog appears
✓ Tab switches to Login
✓ Check database:
  SELECT * FROM users WHERE email='member@test.com';
✓ is_approved should be FALSE
```

#### Test 1.3: Rejected Signup (Invalid Team ID)
```
Scenario: User tries to sign up with non-existent team ID
Steps:
1. Sign Up tab
2. Enter valid user info but Team ID: "99-9999"
3. Click Sign Up
Expected: Error dialog "Team ID not found"

Validation:
✓ Error message appears
✓ Account NOT created in database
```

#### Test 1.4: Pending Approval Access
```
Scenario: Pending user cannot login until approved
Steps:
1. Create pending user (is_approved=FALSE)
2. Try to login with that account
3. Click Login
Expected: "Account pending approval" message

Validation:
✓ Access denied message shown
✓ User not logged in
```

### 2. Admin Dashboard

#### Test 2.1: Create Team
```
Scenario: Admin creates a new team
Steps:
1. Login as admin
2. Team Management tab → Create Team button
3. Enter:
   - Team Name: "Bravo Team"
   - Team ID: "02-0002"
   - Division: "Division A"
4. Click Create
Expected: Success message, team appears in list

Validation:
✓ Team added to table
✓ Database check: SELECT * FROM teams WHERE team_id='02-0002';
✓ New signup uses new team ID
```

#### Test 2.2: Approve User
```
Scenario: Admin approves pending user
Steps:
1. User Approvals tab
2. Find pending user in table
3. Click Approve button
Expected: Success message, user removed from pending list

Validation:
✓ User removed from pending table
✓ Database: is_approved = TRUE
✓ Audit log recorded: SELECT * FROM audit_logs WHERE action='approve';
```

#### Test 2.3: Reject User
```
Scenario: Admin rejects pending user
Steps:
1. User Approvals tab
2. Find pending user
3. Click Reject button
Expected: Success message, user removed

Validation:
✓ User removed from pending list
✓ User completely deleted from database
✓ Audit log shows rejection
```

#### Test 2.4: Change User Role
```
Scenario: Admin changes member's role to captain
Steps:
1. Member Management tab
2. Select user → Change Role button
3. Select "Captain" from dropdown
4. Click Save
Expected: Success message, role updated in table

Validation:
✓ Role changes to Captain in table
✓ Database: role='captain'
✓ Audit log: log shows role change
```

#### Test 2.5: View Audit Log
```
Scenario: Admin views activity log
Steps:
1. Activity Log tab
2. Review recent actions
Expected: See list of actions with timestamps

Validation:
✓ Log entries displayed
✓ Contains user, action, resource type
✓ Timestamps are accurate
✓ Recent actions visible
```

### 3. Member Dashboard

#### Test 3.1: View Checklists
```
Scenario: Member views available checklists
Steps:
1. Login as approved member
2. Checklists tab
3. View checklist list
Expected: List of checklists appears

Validation:
✓ Checklists populated from database
✓ Can click to select checklist
✓ Details and items display
```

#### Test 3.2: Mark Checklist Item
```
Scenario: Member marks an item as completed
Steps:
1. Select checklist
2. Find item in table
3. Change status dropdown to "Completed"
Expected: Status updates immediately

Validation:
✓ Status changes in table
✓ Database: SELECT * FROM checklist_status WHERE status='completed';
✓ Progress bar updates
✓ Audit log recorded
```

#### Test 3.3: Add Checklist Notes
```
Scenario: Member adds notes to a checklist item
Steps:
1. Select checklist item
2. Change status and add notes
3. Notes auto-save
Expected: Notes persisted

Validation:
✓ Notes visible in checklist_status.notes field
✓ Persist across logout/login
```

#### Test 3.4: Create README
```
Scenario: Member creates team documentation
Steps:
1. READMEs tab → Create README
2. Enter:
   - Title: "Ubuntu Hardening Guide"
   - OS Type: "Ubuntu 20.04"
   - Content: "Step 1: Update system..."
3. Click Create
Expected: Success message, README added

Validation:
✓ README appears in team list
✓ Database: SELECT * FROM readmes WHERE title='Ubuntu Hardening Guide';
✓ Other team members can see it
```

#### Test 3.5: Create Encrypted Note
```
Scenario: Member creates encrypted note
Steps:
1. Notes tab → Create Note
2. Enter:
   - Title: "Secret Password"
   - Type: "Password Change"
   - Content: "root:NewPassword123"
   - Check "Encrypt this note"
3. Enter encryption password: "MyPassword"
4. Click Create
Expected: Note created and encrypted

Validation:
✓ Note added to list
✓ Database: is_encrypted=TRUE
✓ Content is encrypted (not plaintext)
✓ encryption_key_salt populated
✓ Try to decrypt with correct password - succeeds
✓ Try to decrypt with wrong password - fails gracefully
```

### 4. Data Integrity Tests

#### Test 4.1: Foreign Key Constraints
```
Scenario: Verify foreign key relationships
Steps:
1. Create user with non-existent team_id
Expected: Database error

Validation:
✓ Cannot insert user with invalid team_id
✓ Foreign key constraint enforced
```

#### Test 4.2: Unique Constraints
```
Scenario: Try to create duplicate team ID
Steps:
1. Admin → Create Team with existing ID
Expected: Error dialog

Validation:
✓ Error shown
✓ Team not duplicated in database
```

#### Test 4.3: Cascade Delete
```
Scenario: Delete team removes all associated data
Steps:
1. Create team with members and data
2. Admin → Delete team
Expected: Team and all related data deleted

Validation:
✓ Team deleted from teams table
✓ Associated users deleted/updated
✓ No orphaned records left
```

## Performance Tests

### Test Load Times
```bash
# Measure login time
time python -c "from app.security import PasswordManager; PasswordManager.hash_password('test')"
# Expected: < 1 second

# Measure database query time
time mysql -u root -p cyberpatriot_runbook -e "SELECT * FROM audit_logs;"
# Expected: < 100ms for 100 rows
```

### Test Memory Usage
```bash
# Monitor memory while app runs
import psutil
# Expected: < 200MB RAM

# Monitor database connections
SHOW PROCESSLIST;
# Expected: Single connection
```

## Security Tests

### Test 4.1: Password Hashing
```python
from app.security import PasswordManager

# Test hash generation
password = "MySecurePassword123"
hash1 = PasswordManager.hash_password(password)
hash2 = PasswordManager.hash_password(password)

# Hashes should be different (salt included)
assert hash1 != hash2

# Verify should work for both
assert PasswordManager.verify_password(password, hash1)
assert PasswordManager.verify_password(password, hash2)

# Wrong password should fail
assert not PasswordManager.verify_password("WrongPassword", hash1)

print("✓ Password hashing tests passed")
```

### Test 4.2: Note Encryption
```python
from app.security import EncryptionManager

# Test encryption/decryption
original = "Secret note content"
password = "encryption_password"

# Encrypt
encrypted, salt = EncryptionManager.encrypt_note(original, password)

# Encrypted should not be readable
assert encrypted != original
assert "Secret" not in encrypted

# Decrypt with correct password
decrypted = EncryptionManager.decrypt_note(encrypted, password, salt)
assert decrypted == original

# Decrypt with wrong password
try:
    EncryptionManager.decrypt_note(encrypted, "wrong_password", salt)
    assert False, "Should have raised error"
except ValueError:
    pass  # Expected

print("✓ Encryption tests passed")
```

### Test 4.3: SQL Injection Protection
```
Scenario: Attempt SQL injection in login
Steps:
1. Email field: "admin' OR '1'='1"
2. Password: anything
3. Click Login
Expected: User not found error (no injection)

Validation:
✓ SQLAlchemy parameterized queries prevent injection
✓ No unexpected data accessed
```

## Deployment Tests

### Test 5.1: Docker Build
```bash
# Build Docker image
docker build -t cyberpatriot-runbook .

# Run with docker-compose
docker-compose up

# Verify container running
docker ps | grep cyberpatriot

# Check logs
docker-compose logs app
```

### Test 5.2: Raspberry Pi Deployment
```bash
# SSH into Raspberry Pi
ssh pi@raspberry-pi-ip

# Check service status
sudo systemctl status cyberpatriot-runbook

# View service logs
sudo journalctl -u cyberpatriot-runbook -f

# Verify application is responding
curl http://localhost:6000/health
```

## Browser Compatibility (if web version added)
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge

## Accessibility Tests
- [ ] Keyboard navigation works
- [ ] Tab order is logical
- [ ] Error messages are clear
- [ ] Color contrast is sufficient

## Final Validation Checklist

```
CORE FUNCTIONALITY
✓ Application starts without errors
✓ Database connections working
✓ All GUI windows render correctly
✓ All buttons are clickable
✓ All forms validate input

AUTHENTICATION
✓ Login works with correct credentials
✓ Login fails with incorrect credentials
✓ Signup validates inputs
✓ Admin users can login immediately
✓ Member users must be approved

ADMIN FEATURES
✓ Can create teams
✓ Can approve users
✓ Can reject users
✓ Can change user roles
✓ Can remove users
✓ Can view audit logs
✓ Can edit team information

MEMBER FEATURES
✓ Can view checklists
✓ Can mark checklist items
✓ Can add notes to items
✓ Can create READMEs
✓ Can view team READMEs
✓ Can create notes
✓ Can encrypt notes
✓ Can logout

SECURITY
✓ Passwords are hashed
✓ Notes can be encrypted
✓ Audit logs are created
✓ Role-based access works
✓ SQL injection prevented
✓ Session management works

DATABASE
✓ All tables created
✓ Foreign keys work
✓ Unique constraints work
✓ Cascade deletes work
✓ Data persists across restarts
✓ Timestamps are accurate

PERFORMANCE
✓ Login completes < 2 seconds
✓ Dashboard loads < 3 seconds
✓ Table scrolling is smooth
✓ No memory leaks detected
✓ Can handle 1000+ audit logs
```

## Sign-Off

- [ ] All tests passed
- [ ] No critical bugs found
- [ ] Performance acceptable
- [ ] Security validated
- [ ] Documentation complete
- [ ] Ready for production

**Test Date**: ______________  
**Tested By**: ______________  
**Sign-Off**: ______________

---

For issues found, create GitHub issues with:
1. Test scenario
2. Expected vs actual behavior
3. Steps to reproduce
4. Error messages/logs
5. Environment details

# Error Fix Guide

## Foreign Key Constraint Error (1452)
**Error Message:** 
```
An error occurred during signup: 1452 (23000): Cannot add or update a child row: 
a foreign key constraint fails
```

### Root Cause
When signing up as Admin/Coach, the app tried to insert into `team_members` table with `team_id=1`, but team 1 didn't exist in the `teams` table.

### Solution Applied
The `create_user()` method now:
1. **Checks if team 1 exists** before using it
2. **Auto-creates a default team** if team 1 doesn't exist
3. **Validates team_id** for competitor/team_captain roles

### To Manually Fix If Needed

If you see this error again, run this SQL:

```sql
-- Create a default team for admin/coach users
INSERT INTO teams (id, name, team_code, division, created_by_user_id)
VALUES (1, 'Default Team', 'DEFAULT1', 'Open', NULL);
```

Or if team 1 already exists but needs fixing:

```sql
-- View all teams
SELECT * FROM teams;

-- View all team_members
SELECT * FROM team_members;

-- Delete orphaned team_members (referencing non-existent teams)
DELETE FROM team_members WHERE team_id NOT IN (SELECT id FROM teams);
```

### What the Fix Does

When a new user signs up:

- **For Admin/Coach roles:**
  - Checks if team ID 1 exists
  - If YES → uses team 1
  - If NO → auto-creates "Default Team" with ID 1
  - Then inserts team membership with the valid team_id

- **For Competitor/Team Captain/Mentor roles:**
  - Requires valid team_id from user input
  - Validates team exists before signup
  - Only proceeds if team is found

This ensures **no foreign key violations** when inserting into `team_members`.

### Testing the Fix

1. Try signing up as Admin → Should work now
2. Try signing up as Competitor without valid team → Shows error message
3. Try signing up as Competitor with valid team → Should work

The error is now fixed in `auth.py` line 98-163 in the `create_user()` method.

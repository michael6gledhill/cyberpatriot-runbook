# Roles & Permissions

| Role     | Create Team | Approve Users | Approve Join Requests | Manage Members | View Audit Log |
|----------|-------------|---------------|-----------------------|----------------|----------------|
| Admin    | Yes         | Yes           | Yes                   | Yes            | Yes            |
| Coach    | Yes         | Yes (team)    | Yes (team)            | Yes (team)     | Yes (team)     |
| Captain  | No          | Pending flow  | Pending flow          | Limited        | No             |
| Member   | No          | No            | Request join          | No             | No             |

Notes:
- Admins can create teams and manage all users/teams.
- Coaches can create teams; they are set as `created_by_user_id`.
- Members/Captains require approval and cannot create teams.

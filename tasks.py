"""
Build a Python application using PySide6 for the GUI and SQLite for the database.
The application should allow multiple user roles with different permissions:

1. Roles:
   - Admin: can see and edit all users and teams.
   - Coach: can see and edit only their team, can create teams, must be approved by Admin.
   - Team Captain: can see and edit only their team, can approve competitors and mentors, must be approved by Coach.
   - Mentor: can see and edit only their team, must be approved by Coach.
   - Competitor: can see their team, must be approved by Coach or Team Captain.

2. User Signup:
   - Fields: name, username, password, role selection, team ID if role < Coach.
   - Role names in DB: admin, coach, team captain, mentor, competitor.
   - Coaches and Admins can create teams. When a coach creates a team, they are automatically added to that team.
   - Approval system: Coaches need Admin approval, Team Captains and Mentors need Coach approval, Competitors need Coach or Team Captain approval.

3. Login:
   - Users must log in with username and password.
   - Settings page before login to set server IP, server username/password, and database name.

4. Database:
   - Robust structure to handle users, roles, teams, checklists, readmes, forensic questions, and personal notes.
   - Users table, teams table, checklists table, checklist_items table, readmes table, forensic_questions table, notes table.
   - Access controls based on role and team affiliation.

5. GUI Features:
   - Create account window with role selection and appropriate fields.
   - Admin dashboard: see/edit all users.
   - Coach/Team Captain dashboard: see/edit their team, approve new members.
   - Checklist section:
       * Coaches or Team Captains create checklists with items.
       * Checklist items have: name, description, steps (how to do it).
       * Competitors/Mentors can edit checklist items and push changes (like GitHub).
       * Edits require approval by Team Captain or Mentor.
       * When completing a checklist, show all items, highlight current item, allow marking as completed/skipped/not completed.
       * Click to expand description and steps.
   - Readmes: Upload/view team readmes, visible to all team members.
   - Forensic questions: Users can ask questions visible to the whole team.
   - Notes: Personal notes, persistent between logins, only visible to the creator.
   - Team-based access: Only team-specific data is visible to coaches, captains, mentors, and competitors. Data isolation for multiple teams.

6. GitHub & Documentation Integration:
   - Create Quarto Markdown (.qmd) files for all app documentation (installation, usage, features, database schema).
   - Create a Quarto YAML file (.yml) to configure deployment to GitHub Pages.
   - Make sure docs are linked to the project repository structure so they can be built automatically with Quarto and deployed to GitHub Pages.

7. Additional Features Suggestions (optional but recommended):
   - Search/filter users, checklists, or notes.
   - Notifications for approvals.
   - Activity log for changes to checklists and readmes.
   - Export/import checklists and readmes.
   - Password reset functionality.
   - Option to assign multiple Team Captains per team.
   - Visual dashboard showing team progress on checklists.

Start by creating:
- The SQLite database schema with all tables and relations.
- The signup/login GUI using PySide6.
- Role-based dashboards and access logic.
- Quarto Markdown documentation files and YAML file for GitHub Pages deployment.
- Include comments describing each GUI window, database operation, and documentation section.
"""

---
title: Database Schema
---

# Database Schema

Tables:
- `users(id, name, username, password_hash, role, team_id, approved, created_at)`
- `teams(id, name, created_by, created_at)`
- `checklists(id, team_id, name, description, created_by, created_at)`
- `checklist_items(id, checklist_id, item_name, description, steps, status, created_at)`
- `readmes(id, team_id, title, content, created_by, created_at)`
- `forensic_questions(id, team_id, question, answer, asked_by, answered_by, created_at)`
- `notes(id, user_id, team_id, title, content, created_at)`

Relationships:
- `users.team_id -> teams.id`
- `checklists.team_id -> teams.id`
- `checklist_items.checklist_id -> checklists.id`
- `readmes.team_id -> teams.id`
- `forensic_questions.team_id -> teams.id`
- `notes.user_id -> users.id`

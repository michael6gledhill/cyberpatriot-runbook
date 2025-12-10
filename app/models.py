"""
Data models and CRUD helpers for users, teams, checklists, readmes,
forensic questions, and notes. Minimal implementations to support the GUI.
"""
import hashlib
from typing import Optional, List, Dict, Any
from .db import get_conn


def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


# Users

def create_user(name: str, username: str, password: str, role: str, team_id: Optional[int] = None, approved: int = 0) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, username, password_hash, role, team_id, approved) VALUES (?,?,?,?,?,?)",
        (name, username, _hash_password(password), role, team_id, approved),
    )
    conn.commit()
    user_id = int(cur.lastrowid or 0)
    conn.close()
    return user_id


def approve_user(user_id: int):
    conn = get_conn()
    conn.execute("UPDATE users SET approved=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


def get_user_by_credentials(username: str, password: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id,name,username,role,team_id,approved FROM users WHERE username=? AND password_hash=?",
                (username, _hash_password(password)))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    keys = ["id", "name", "username", "role", "team_id", "approved"]
    return dict(zip(keys, row))


# Teams

def create_team(name: str, created_by_user_id: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO teams (name, created_by) VALUES (?,?)", (name, created_by_user_id))
    team_id = int(cur.lastrowid or 0)
    # add creator to team if coach
    cur.execute("UPDATE users SET team_id=? WHERE id=?", (team_id, created_by_user_id))
    conn.commit()
    conn.close()
    return team_id


def list_team_users(team_id: int) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id,name,username,role,approved FROM users WHERE team_id=?", (team_id,))
    rows = cur.fetchall()
    conn.close()
    keys = ["id", "name", "username", "role", "approved"]
    return [dict(zip(keys, r)) for r in rows]


# Checklists

def create_checklist(team_id: int, name: str, description: str, created_by: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO checklists (team_id, name, description, created_by) VALUES (?,?,?,?)",
                (team_id, name, description, created_by))
    cid = int(cur.lastrowid or 0)
    conn.commit()
    conn.close()
    return cid


def add_checklist_item(checklist_id: int, item_name: str, description: str, steps: str, status: str = "not completed") -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO checklist_items (checklist_id, item_name, description, steps, status) VALUES (?,?,?,?,?)",
                (checklist_id, item_name, description, steps, status))
    iid = int(cur.lastrowid or 0)
    conn.commit()
    conn.close()
    return iid


# Readmes

def add_readme(team_id: int, title: str, content: str, created_by: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO readmes (team_id, title, content, created_by) VALUES (?,?,?,?)",
                (team_id, title, content, created_by))
    rid = int(cur.lastrowid or 0)
    conn.commit()
    conn.close()
    return rid


# Forensic Qs

def ask_forensic_question(team_id: int, question: str, asked_by: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO forensic_questions (team_id, question, asked_by) VALUES (?,?,?)",
                (team_id, question, asked_by))
    qid = int(cur.lastrowid or 0)
    conn.commit()
    conn.close()
    return qid


def answer_forensic_question(qid: int, answer: str, answered_by: int):
    conn = get_conn()
    conn.execute("UPDATE forensic_questions SET answer=?, answered_by=? WHERE id=?", (answer, answered_by, qid))
    conn.commit()
    conn.close()


# Notes

def add_note(user_id: int, team_id: int, title: str, content: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (user_id, team_id, title, content) VALUES (?,?,?,?)",
                (user_id, team_id, title, content))
    nid = int(cur.lastrowid or 0)
    conn.commit()
    conn.close()
    return nid

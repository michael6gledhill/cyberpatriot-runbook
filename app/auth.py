"""
Authentication and role-based approval rules.
"""
from typing import Optional, Dict, Any
from .models import create_user, get_user_by_credentials


def signup(name: str, username: str, password: str, role: str, team_id: Optional[int]) -> int:
    """
    Create user with approval defaults:
    - coach: requires admin approval (approved=0)
    - team captain / mentor: requires coach approval (approved=0)
    - competitor: requires team captain or coach approval (approved=0)
    - admin: approved immediately (approved=1)
    """
    approved = 1 if role == "admin" else 0
    return create_user(name, username, password, role, team_id, approved)


def login(username: str, password: str) -> Optional[Dict[str, Any]]:
    return get_user_by_credentials(username, password)

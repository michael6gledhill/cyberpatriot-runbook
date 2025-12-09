#!/usr/bin/env python
"""Test script to debug session issues."""

from app.database import init_db
from app.database.repositories import TeamRepository, UserRepository

db_url = "mysql+pymysql://root:h0gBog89!@localhost:3306/cyberpatriot_runbook"
init_db(db_url)

print("Testing team retrieval...")
try:
    team = TeamRepository.get_team_by_team_id("01-0001")
    if team:
        print(f"✓ Team found: {team.name} (ID: {team.id})")
        print(f"✓ Created by user ID: {team.created_by_user_id}")
        print(f"✓ Team attributes accessible!")
    else:
        print("✗ No team found with ID 01-0001")
except Exception as e:
    print(f"✗ Error retrieving team: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting user retrieval...")
try:
    user = UserRepository.get_user_by_email("admin@cyberpatriot.local")
    if user:
        print(f"✓ User found: {user.name}")
        print(f"✓ User role: {user.role}")
        print(f"✓ User attributes accessible!")
    else:
        print("✗ No user found")
except Exception as e:
    print(f"✗ Error retrieving user: {e}")
    import traceback
    traceback.print_exc()

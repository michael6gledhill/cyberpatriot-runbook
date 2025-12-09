#!/usr/bin/env python3
"""
CyberPatriot Runbook - Database Initialization Script
This script initializes the database with sample data and creates the first admin user.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def initialize_database():
    """Initialize the database with sample data"""
    
    print("=" * 70)
    print("  CyberPatriot Runbook - Database Initialization")
    print("=" * 70)
    print()
    
    # Import after adding to path
    try:
        from app.database import DatabaseConfig
        from app.models import User, Team, AuditLog
        from app.security import PasswordManager
        print("✅ Successfully imported application modules")
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    
    try:
        # Initialize database
        print("\n1. Initializing database connection...")
        db_config = DatabaseConfig()
        
        # Create tables
        print("   Creating tables...")
        db_config.create_all_tables()
        print("   ✅ Tables created successfully")
        
        # Check if tables are empty
        session = db_config.get_session()
        team_count = session.query(Team).count()
        user_count = session.query(User).count()
        session.close()
        
        if team_count == 0 and user_count == 0:
            print("\n2. Creating sample data...")
            
            session = db_config.get_session()
            try:
                # Create sample team
                team = Team(
                    name="Blue Squadron",
                    team_id="01-0001",
                    division="CivilAirPatrol"
                )
                session.add(team)
                session.flush()
                print("   ✅ Sample team created: Blue Squadron (01-0001)")
                
                # Create admin user
                admin_email = "admin@cyberpatriot.local"
                admin_password = "Admin@123"
                
                admin_user = User(
                    name="Admin User",
                    email=admin_email,
                    password_hash=PasswordManager.hash_password(admin_password),
                    role="admin",
                    is_approved=True,
                    is_active=True,
                    team=team
                )
                session.add(admin_user)
                session.flush()
                print(f"   ✅ Admin user created: {admin_email}")
                print(f"      Default password: {admin_password}")
                print("      ⚠️  PLEASE CHANGE THIS PASSWORD ON FIRST LOGIN!")
                
                # Log initialization
                audit_log = AuditLog(
                    user_id=admin_user.id,
                    action="DATABASE_INITIALIZATION",
                    resource_type="SYSTEM",
                    description="Database initialized with sample data"
                )
                session.add(audit_log)
                
                session.commit()
                print("\n   ✅ Sample data committed successfully")
                
            except Exception as e:
                session.rollback()
                print(f"   ❌ Error creating sample data: {e}")
                return False
            finally:
                session.close()
        else:
            print("\n2. Database already contains data")
            print(f"   Teams: {team_count}")
            print(f"   Users: {user_count}")
            print("   (Skipping sample data creation)")
        
        print("\n3. Verifying database structure...")
        session = db_config.get_session()
        try:
            team_count = session.query(Team).count()
            user_count = session.query(User).count()
            audit_count = session.query(AuditLog).count()
            
            print(f"   Teams: {team_count}")
            print(f"   Users: {user_count}")
            print(f"   Audit Logs: {audit_count}")
            print("   ✅ Database structure verified")
        finally:
            session.close()
        
        print("\n" + "=" * 70)
        print("✅ Database initialization complete!")
        print("=" * 70)
        print()
        print("You can now:")
        print("  1. Run the application: python main.py")
        print("  2. Login with: admin@cyberpatriot.local / Admin@123")
        print("  3. Change your password on first login")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    success = initialize_database()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

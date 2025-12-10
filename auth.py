"""
Login/Signup Application for CyberPatriot Runbook
Handles user authentication and registration with role-based workflow
"""
import hashlib
import getpass
import sys
from datetime import datetime
from db_config import get_connection, close_connection

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def clear_screen():
    """Clear the terminal screen"""
    import os
    os.system('cls' if sys.platform == 'win32' else 'clear')

def print_header(title):
    """Print a formatted header"""
    clear_screen()
    print("=" * 60)
    print(f" {title}".center(60))
    print("=" * 60)
    print()

def user_exists(connection, username):
    """Check if a username already exists in the database"""
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()

def add_roles_if_needed(connection):
    """Ensure all role types exist in the database"""
    cursor = connection.cursor()
    roles = ['admin', 'coach', 'team_captain', 'mentor', 'competitor']
    
    try:
        for role in roles:
            cursor.execute("SELECT id FROM roles WHERE name = %s", (role,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO roles (name) VALUES (%s)", (role,))
        connection.commit()
    finally:
        cursor.close()

def get_role_id(connection, role_name):
    """Get the role ID from the role name"""
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()

def signup():
    """Handle user signup"""
    print_header("SIGN UP")
    
    connection = get_connection()
    if not connection:
        print("Error: Cannot connect to database")
        return False
    
    try:
        # Ensure roles exist
        add_roles_if_needed(connection)
        
        # Collect user information
        print("Please provide the following information:\n")
        
        # Full name
        full_name = input("Full Name: ").strip()
        if not full_name:
            print("\nError: Full name cannot be empty")
            return False
        
        # Username
        while True:
            username = input("Username: ").strip()
            if not username:
                print("Error: Username cannot be empty")
                continue
            if user_exists(connection, username):
                print("Error: Username already exists")
                continue
            break
        
        # Password
        while True:
            password = getpass.getpass("Password: ")
            if not password:
                print("Error: Password cannot be empty")
                continue
            confirm_password = getpass.getpass("Confirm Password: ")
            if password != confirm_password:
                print("Error: Passwords do not match")
                continue
            break
        
        # User Type selection
        print("\nSelect User Type:")
        print("1. Admin")
        print("2. Coach")
        print("3. Team Captain")
        print("4. Mentor")
        print("5. Competitor")
        
        user_type_map = {
            '1': 'admin',
            '2': 'coach',
            '3': 'team_captain',
            '4': 'mentor',
            '5': 'competitor'
        }
        
        while True:
            user_type_choice = input("\nEnter your choice (1-5): ").strip()
            if user_type_choice in user_type_map:
                user_type = user_type_map[user_type_choice]
                break
            print("Error: Invalid choice. Please enter 1-5")
        
        # Team ID (required for team captain, mentor, competitor)
        team_id = None
        if user_type in ['team_captain', 'mentor', 'competitor']:
            while True:
                try:
                    team_id = int(input(f"\nEnter Team ID: ").strip())
                    # Verify team exists
                    cursor = connection.cursor()
                    cursor.execute("SELECT id FROM teams WHERE id = %s", (team_id,))
                    if not cursor.fetchone():
                        print(f"Error: Team ID {team_id} does not exist")
                        cursor.close()
                        continue
                    cursor.close()
                    break
                except ValueError:
                    print("Error: Team ID must be a number")
        
        # Create the user in the database
        cursor = connection.cursor()
        password_hash = hash_password(password)
        
        try:
            cursor.execute(
                """
                INSERT INTO users (name, username, password_hash, email)
                VALUES (%s, %s, %s, %s)
                """,
                (full_name, username, password_hash, f"{username}@cyberpatriot.local")
            )
            user_id = cursor.lastrowid
            
            # Get role ID
            role_id = get_role_id(connection, user_type)
            
            # For admin and coach, no team needed (status = 'approved')
            if user_type in ['admin', 'coach']:
                status = 'approved'
                cursor.execute(
                    """
                    INSERT INTO team_members (user_id, team_id, role_id, status)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, 1, role_id, status)  # Using team_id=1 as default for admin/coach
                )
            else:
                # For team_captain, mentor, competitor, status = 'pending'
                status = 'pending'
                cursor.execute(
                    """
                    INSERT INTO team_members (user_id, team_id, role_id, status)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, team_id, role_id, status)
                )
            
            connection.commit()
            
            print(f"\n{'='*60}")
            if user_type == 'admin':
                print(" Account Created Successfully!".center(60))
                print(" Your admin account is immediately approved.".center(60))
            else:
                print(" Account Created Successfully!".center(60))
                print(f" Your {user_type.replace('_', ' ')} account is pending approval.".center(60))
            print("=" * 60)
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"\nError creating account: {e}")
            return False
        finally:
            cursor.close()
    
    finally:
        close_connection(connection)

def login():
    """Handle user login"""
    print_header("LOGIN")
    
    connection = get_connection()
    if not connection:
        print("Error: Cannot connect to database")
        return False
    
    try:
        username = input("Username: ").strip()
        if not username:
            print("Error: Username cannot be empty")
            return False
        
        password = getpass.getpass("Password: ")
        if not password:
            print("Error: Password cannot be empty")
            return False
        
        # Check credentials
        cursor = connection.cursor()
        try:
            password_hash = hash_password(password)
            cursor.execute(
                "SELECT id, name FROM users WHERE username = %s AND password_hash = %s",
                (username, password_hash)
            )
            result = cursor.fetchone()
            
            if result:
                user_id, name = result
                print(f"\n{'='*60}")
                print(f" Login Successful!".center(60))
                print(f" Welcome, {name}!".center(60))
                print("=" * 60)
                
                # Get user status
                cursor.execute(
                    """
                    SELECT r.name, tm.status 
                    FROM team_members tm
                    JOIN roles r ON tm.role_id = r.id
                    WHERE tm.user_id = %s
                    LIMIT 1
                    """,
                    (user_id,)
                )
                role_result = cursor.fetchone()
                if role_result:
                    role, status = role_result
                    print(f"\nRole: {role.replace('_', ' ').title()}")
                    print(f"Status: {status.upper()}")
                
                input("\nPress Enter to continue...")
                return True
            else:
                print("\n" + "="*60)
                print(" Login Failed".center(60))
                print(" Invalid username or password".center(60))
                print("=" * 60)
                return False
        finally:
            cursor.close()
    
    finally:
        close_connection(connection)

def main():
    """Main application loop"""
    while True:
        print_header("CyberPatriot Runbook - Authentication")
        print("\nOptions:")
        print("1. Login")
        print("2. Sign Up")
        print("3. Exit")
        print()
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            login()
        elif choice == '2':
            signup()
        elif choice == '3':
            print("\nThank you for using CyberPatriot Runbook!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()

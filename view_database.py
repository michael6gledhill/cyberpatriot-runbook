"""
Database Viewer for CyberPatriot Runbook
View and manage all database records including users, teams, roles, and approvals
"""
import sys
from tabulate import tabulate
from db_config import get_connection, close_connection

def clear_screen():
    """Clear the terminal screen"""
    import os
    os.system('cls' if sys.platform == 'win32' else 'clear')

def print_header(title):
    """Print a formatted header"""
    clear_screen()
    print("=" * 100)
    print(f" {title}".center(100))
    print("=" * 100)
    print()

def view_all_users():
    """Display all users in the database"""
    print_header("ALL USERS")
    
    connection = get_connection()
    if not connection:
        print("Error: Cannot connect to database")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT u.id, u.name, u.username, u.email, u.is_active, u.created_at
            FROM users u
            ORDER BY u.created_at DESC
        """)
        
        rows = cursor.fetchall()
        
        if rows:
            headers = ["ID", "Name", "Username", "Email", "Active", "Created At"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
        else:
            print("No users found in the database.")
        
        cursor.close()
    finally:
        close_connection(connection)

def view_user_details():
    """Display detailed information about a specific user"""
    print_header("USER DETAILS")
    
    connection = get_connection()
    if not connection:
        print("Error: Cannot connect to database")
        return
    
    try:
        cursor = connection.cursor()
        
        try:
            user_id = int(input("Enter User ID: "))
        except ValueError:
            print("Error: User ID must be a number")
            return
        
        cursor.execute("""
            SELECT u.id, u.name, u.username, u.email, u.is_active, u.created_at, u.updated_at
            FROM users u
            WHERE u.id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        
        if user:
            print("\n--- User Information ---")
            print(f"ID: {user[0]}")
            print(f"Name: {user[1]}")
            print(f"Username: {user[2]}")
            print(f"Email: {user[3]}")
            print(f"Active: {user[4]}")
            print(f"Created: {user[5]}")
            print(f"Updated: {user[6]}")
            
            # Get team memberships
            cursor.execute("""
                SELECT tm.id, t.name, r.name, tm.status, tm.created_at
                FROM team_members tm
                JOIN teams t ON tm.team_id = t.id
                JOIN roles r ON tm.role_id = r.id
                WHERE tm.user_id = %s
            """, (user_id,))
            
            memberships = cursor.fetchall()
            print("\n--- Team Memberships ---")
            if memberships:
                headers = ["Member ID", "Team Name", "Role", "Status", "Joined"]
                print(tabulate(memberships, headers=headers, tablefmt="grid"))
            else:
                print("No team memberships found.")
        else:
            print(f"User with ID {user_id} not found.")
        
        cursor.close()
    finally:
        close_connection(connection)

def view_teams():
    """Display all teams in the database"""
    print_header("ALL TEAMS")
    
    connection = get_connection()
    if not connection:
        print("Error: Cannot connect to database")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT t.id, t.name, t.team_code, t.division, u.name as created_by, t.created_at
            FROM teams t
            LEFT JOIN users u ON t.created_by_user_id = u.id
            ORDER BY t.created_at DESC
        """)
        
        rows = cursor.fetchall()
        
        if rows:
            headers = ["ID", "Team Name", "Team Code", "Division", "Created By", "Created At"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
        else:
            print("No teams found in the database.")
        
        cursor.close()
    finally:
        close_connection(connection)

def view_team_members():
    """Display all team members with their roles and approval status"""
    print_header("TEAM MEMBERS & APPROVAL STATUS")
    
    connection = get_connection()
    if not connection:
        print("Error: Cannot connect to database")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 
                tm.id,
                u.name,
                u.username,
                t.name as team,
                r.name as role,
                tm.status,
                tm.created_at
            FROM team_members tm
            JOIN users u ON tm.user_id = u.id
            JOIN teams t ON tm.team_id = t.id
            JOIN roles r ON tm.role_id = r.id
            ORDER BY tm.status DESC, t.name, u.name
        """)
        
        rows = cursor.fetchall()
        
        if rows:
            headers = ["Member ID", "User Name", "Username", "Team", "Role", "Status", "Joined"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
            
            # Summary statistics
            cursor.execute("""
                SELECT tm.status, COUNT(*) as count
                FROM team_members tm
                GROUP BY tm.status
            """)
            
            stats = cursor.fetchall()
            print("\n--- Approval Status Summary ---")
            for status, count in stats:
                print(f"{status.upper()}: {count}")
        else:
            print("No team members found in the database.")
        
        cursor.close()
    finally:
        close_connection(connection)

def view_pending_approvals():
    """Display all pending approval requests"""
    print_header("PENDING APPROVALS")
    
    connection = get_connection()
    if not connection:
        print("Error: Cannot connect to database")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 
                tm.id,
                u.name,
                u.username,
                t.name as team,
                r.name as role,
                tm.created_at
            FROM team_members tm
            JOIN users u ON tm.user_id = u.id
            JOIN teams t ON tm.team_id = t.id
            JOIN roles r ON tm.role_id = r.id
            WHERE tm.status = 'pending'
            ORDER BY tm.created_at ASC
        """)
        
        rows = cursor.fetchall()
        
        if rows:
            headers = ["Member ID", "User Name", "Username", "Team", "Role", "Requested"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
            print(f"\nTotal Pending Approvals: {len(rows)}")
        else:
            print("No pending approvals.")
        
        cursor.close()
    finally:
        close_connection(connection)

def view_roles():
    """Display all available roles"""
    print_header("AVAILABLE ROLES")
    
    connection = get_connection()
    if not connection:
        print("Error: Cannot connect to database")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT r.id, r.name, COUNT(tm.id) as user_count
            FROM roles r
            LEFT JOIN team_members tm ON r.id = tm.role_id
            GROUP BY r.id, r.name
            ORDER BY r.id
        """)
        
        rows = cursor.fetchall()
        
        if rows:
            headers = ["Role ID", "Role Name", "User Count"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
        else:
            print("No roles found in the database.")
        
        cursor.close()
    finally:
        close_connection(connection)

def view_statistics():
    """Display database statistics"""
    print_header("DATABASE STATISTICS")
    
    connection = get_connection()
    if not connection:
        print("Error: Cannot connect to database")
        return
    
    try:
        cursor = connection.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Total teams
        cursor.execute("SELECT COUNT(*) FROM teams")
        total_teams = cursor.fetchone()[0]
        
        # Total team members
        cursor.execute("SELECT COUNT(*) FROM team_members")
        total_members = cursor.fetchone()[0]
        
        # Pending approvals
        cursor.execute("SELECT COUNT(*) FROM team_members WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        # Approved members
        cursor.execute("SELECT COUNT(*) FROM team_members WHERE status = 'approved'")
        approved = cursor.fetchone()[0]
        
        # Members by role
        cursor.execute("""
            SELECT r.name, COUNT(tm.id) as count
            FROM roles r
            LEFT JOIN team_members tm ON r.id = tm.role_id
            GROUP BY r.id, r.name
            ORDER BY count DESC
        """)
        role_stats = cursor.fetchall()
        
        print(f"Total Users: {total_users}")
        print(f"Total Teams: {total_teams}")
        print(f"Total Team Members: {total_members}")
        print(f"\nApproval Status:")
        print(f"  - Pending: {pending}")
        print(f"  - Approved: {approved}")
        print(f"\nMembers by Role:")
        for role, count in role_stats:
            print(f"  - {role}: {count}")
        
        cursor.close()
    finally:
        close_connection(connection)

def main():
    """Main application loop"""
    while True:
        print_header("CyberPatriot Runbook - Database Viewer")
        print("\nOptions:")
        print("1. View All Users")
        print("2. View User Details")
        print("3. View All Teams")
        print("4. View Team Members & Status")
        print("5. View Pending Approvals")
        print("6. View Available Roles")
        print("7. View Database Statistics")
        print("8. Exit")
        print()
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == '1':
            view_all_users()
        elif choice == '2':
            view_user_details()
        elif choice == '3':
            view_teams()
        elif choice == '4':
            view_team_members()
        elif choice == '5':
            view_pending_approvals()
        elif choice == '6':
            view_roles()
        elif choice == '7':
            view_statistics()
        elif choice == '8':
            print("\nThank you for using CyberPatriot Runbook Database Viewer!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()

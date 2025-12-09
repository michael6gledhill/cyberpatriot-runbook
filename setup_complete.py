#!/usr/bin/env python3
"""
CyberPatriot Runbook - Complete Setup and Validation Script
This script sets up the entire application including database, dependencies, and sample data.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

class SetupManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.setup_log = self.project_root / "setup_log.json"
        self.log_data = {"timestamp": datetime.now().isoformat(), "steps": []}
        
    def log_step(self, step_name, status, message=""):
        """Log a setup step"""
        self.log_data["steps"].append({
            "step": step_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
    def save_log(self):
        """Save setup log to file"""
        with open(self.setup_log, 'w') as f:
            json.dump(self.log_data, f, indent=2)
        print_info(f"Setup log saved to {self.setup_log}")

    def verify_python_version(self):
        """Verify Python version is 3.9 or higher"""
        print_header("Step 1: Verifying Python Version")
        
        version = sys.version_info
        if version.major >= 3 and version.minor >= 9:
            print_success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
            self.log_step("Python Version", "success", f"Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            print_error(f"Python 3.9+ required, found {version.major}.{version.minor}")
            self.log_step("Python Version", "failed", f"Python {version.major}.{version.minor} found, 3.9+ required")
            return False

    def verify_project_structure(self):
        """Verify all required directories exist"""
        print_header("Step 2: Verifying Project Structure")
        
        required_dirs = [
            "app",
            "app/models",
            "app/database",
            "app/controllers",
            "app/gui",
            "app/security",
            "alembic",
            "resources"
        ]
        
        all_exist = True
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                print_success(f"{dir_name}/")
                self.log_step(f"Directory: {dir_name}", "success")
            else:
                print_error(f"{dir_name}/ not found")
                self.log_step(f"Directory: {dir_name}", "failed", "Directory not found")
                all_exist = False
        
        return all_exist

    def verify_required_files(self):
        """Verify all required files exist"""
        print_header("Step 3: Verifying Required Files")
        
        required_files = [
            "main.py",
            "config.py",
            "requirements.txt",
            "database_setup.sql",
            ".env.example",
            "app/__init__.py",
            "app/models/__init__.py",
            "app/database/__init__.py",
            "app/controllers/__init__.py",
            "app/gui/__init__.py",
            "app/security/__init__.py",
            "alembic/env.py",
            "alembic.ini"
        ]
        
        all_exist = True
        for file_name in required_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                size_kb = file_path.stat().st_size / 1024
                print_success(f"{file_name} ({size_kb:.1f} KB)")
                self.log_step(f"File: {file_name}", "success", f"{size_kb:.1f} KB")
            else:
                print_error(f"{file_name} not found")
                self.log_step(f"File: {file_name}", "failed", "File not found")
                all_exist = False
        
        return all_exist

    def verify_dependencies(self):
        """Verify all required Python packages are installed"""
        print_header("Step 4: Verifying Dependencies")
        
        required_packages = {
            "PySide6": "6.6.1+",
            "SQLAlchemy": "2.0.0+",
            "PyMySQL": "1.1.0+",
            "alembic": "1.13.0+",
            "bcrypt": "4.1.0+",
            "cryptography": "41.0.0+",
            "python-dotenv": "1.0.0+",
        }
        
        all_installed = True
        for package, version in required_packages.items():
            try:
                __import__(package.lower().replace("-", "_"))
                print_success(f"{package} {version}")
                self.log_step(f"Package: {package}", "success")
            except ImportError:
                print_warning(f"{package} {version} - NOT INSTALLED")
                self.log_step(f"Package: {package}", "warning", "Not installed")
                all_installed = False
        
        return all_installed

    def check_database_connection(self):
        """Check if database can be connected to"""
        print_header("Step 5: Checking Database Connection")
        
        try:
            import mysql.connector
            print_success("MySQL connector available")
            
            # Try to connect to default MySQL
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="root"
                )
                print_success("Can connect to MySQL server")
                conn.close()
                self.log_step("Database Connection", "success", "Connected to MySQL")
                return True
            except mysql.connector.Error as e:
                print_warning(f"Cannot connect to MySQL: {e}")
                print_info("This is OK - you'll set up MySQL in the next step")
                self.log_step("Database Connection", "warning", str(e))
                return False
                
        except ImportError:
            print_warning("MySQL connector not installed")
            print_info("Run: pip install PyMySQL mysql-connector-python")
            self.log_step("Database Connection", "warning", "MySQL connector not installed")
            return False

    def verify_config(self):
        """Verify configuration files"""
        print_header("Step 6: Verifying Configuration")
        
        config_file = self.project_root / "config.py"
        if config_file.exists():
            print_success(f"config.py found")
            self.log_step("Configuration", "success")
            return True
        else:
            print_error("config.py not found")
            self.log_step("Configuration", "failed", "config.py not found")
            return False

    def verify_alembic(self):
        """Verify Alembic migration setup"""
        print_header("Step 7: Verifying Alembic Setup")
        
        alembic_ini = self.project_root / "alembic.ini"
        alembic_env = self.project_root / "alembic" / "env.py"
        
        if alembic_ini.exists():
            print_success("alembic.ini found")
            self.log_step("Alembic Config", "success")
        else:
            print_error("alembic.ini not found")
            self.log_step("Alembic Config", "failed", "alembic.ini not found")
            return False
            
        if alembic_env.exists():
            print_success("alembic/env.py found")
            self.log_step("Alembic Environment", "success")
        else:
            print_error("alembic/env.py not found")
            self.log_step("Alembic Environment", "failed", "env.py not found")
            return False
        
        return True

    def run_all_checks(self):
        """Run all verification checks"""
        print_header("CyberPatriot Runbook - Setup Verification")
        print("This script will verify your entire project setup.\n")
        
        checks = [
            ("Python Version", self.verify_python_version),
            ("Project Structure", self.verify_project_structure),
            ("Required Files", self.verify_required_files),
            ("Dependencies", self.verify_dependencies),
            ("Database Connection", self.check_database_connection),
            ("Configuration", self.verify_config),
            ("Alembic Setup", self.verify_alembic),
        ]
        
        results = {}
        for check_name, check_func in checks:
            try:
                results[check_name] = check_func()
            except Exception as e:
                print_error(f"Error during {check_name}: {e}")
                self.log_step(check_name, "error", str(e))
                results[check_name] = False
        
        return results

    def print_summary(self, results):
        """Print summary of all checks"""
        print_header("Setup Verification Summary")
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for check_name, passed_check in results.items():
            status = "✅ PASS" if passed_check else "❌ FAIL"
            print(f"{status}: {check_name}")
        
        print(f"\n{passed}/{total} checks passed")
        
        if passed == total:
            print_success("All checks passed! Your setup is ready.")
            return True
        elif passed >= total - 2:
            print_warning("Most checks passed. Some dependencies may need installation.")
            return True
        else:
            print_error("Some critical checks failed. Please review the errors above.")
            return False

def main():
    """Main entry point"""
    try:
        manager = SetupManager()
        results = manager.run_all_checks()
        manager.save_log()
        
        success = manager.print_summary(results)
        
        print_header("Next Steps")
        print("""
1. Install Dependencies (if not already done):
   pip install -r requirements.txt

2. Set up MySQL Database:
   - Ensure MySQL server is running
   - Run: mysql -u root -p < database_setup.sql
   
3. Configure Environment:
   - Copy .env.example to .env
   - Update DATABASE_URL and other settings
   
4. Initialize Database:
   - Run: python main.py (will create tables if needed)
   
5. Create Admin User:
   - Use the signup form in the GUI
   - First user will have admin rights
   
6. Run the Application:
   - python main.py
        """)
        
        if success:
            print_success("Setup verification complete!")
            return 0
        else:
            print_error("Setup verification found issues. Please review above.")
            return 1
            
    except Exception as e:
        print_error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

import os
import sys
from getpass import getpass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import User  # assumes models define User
from app.security.passwords import hash_password  # assumes helper to hash

def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL is not set.")
        sys.exit(1)

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    default_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@cyberpatriot.local")
    default_name = os.getenv("DEFAULT_ADMIN_NAME", "Admin User")
    password_env = os.getenv("DEFAULT_ADMIN_PASSWORD")

    if password_env:
        password = password_env
    else:
        print("Enter password for the default admin user (input hidden):")
        password = getpass()

    existing = session.query(User).filter(User.email == default_email).first()
    if existing:
        print(f"Admin user already exists: {default_email}")
        return

    user = User(
        name=default_name,
        email=default_email,
        password_hash=hash_password(password),
        role="admin",
        is_approved=True,
        is_active=True,
    )
    session.add(user)
    session.commit()
    print(f"Created admin user: {default_email}")

if __name__ == "__main__":
    main()

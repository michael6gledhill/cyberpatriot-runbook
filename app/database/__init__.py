"""Database configuration and session management."""

import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

from app.models.base import Base


class DatabaseConfig:
    """Database configuration manager."""

    def __init__(self, db_url: Optional[str] = None):
        """Initialize database configuration.

        Args:
            db_url: Database URL. If None, uses environment variable or default SQLite.
        """
        if db_url is None:
            db_url = os.getenv(
                "DATABASE_URL",
                "mysql+pymysql://root:password@localhost:3306/cyberpatriot_runbook"
            )

        self.db_url = db_url
        self.engine = None
        self.SessionLocal = None

    def initialize(self):
        """Initialize database engine and session factory."""
        # Use check_same_thread for SQLite, remove for production MySQL
        if "sqlite" in self.db_url:
            self.engine = create_engine(
                self.db_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            self.engine = create_engine(
                self.db_url,
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,   # Recycle connections after 1 hour
            )

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

    def create_tables(self):
        """Create all tables in the database."""
        if self.engine is None:
            self.initialize()
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables in the database (for testing/reset)."""
        if self.engine is None:
            self.initialize()
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Session:
        """Get a database session context manager.

        Yields:
            SQLAlchemy Session object
        """
        if self.SessionLocal is None:
            self.initialize()

        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session_sync(self) -> Session:
        """Get a synchronous database session.

        Returns:
            SQLAlchemy Session object
        """
        if self.SessionLocal is None:
            self.initialize()
        return self.SessionLocal()


# Global database instance
_db_config = None


def get_db_config() -> DatabaseConfig:
    """Get the global database configuration instance."""
    global _db_config
    if _db_config is None:
        _db_config = DatabaseConfig()
        _db_config.initialize()
    return _db_config


def get_session() -> Session:
    """Get a new database session."""
    return get_db_config().get_session_sync()


def init_db(db_url: Optional[str] = None):
    """Initialize the database with optional custom URL."""
    global _db_config
    _db_config = DatabaseConfig(db_url)
    _db_config.initialize()
    _db_config.create_tables()

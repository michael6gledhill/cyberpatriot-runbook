"""Application initialization module."""

from app.database import init_db, get_db_config

__all__ = ["init_db", "get_db_config"]

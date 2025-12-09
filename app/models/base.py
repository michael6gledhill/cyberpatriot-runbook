"""Base model class for all database models."""

from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

"""User model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import enum

from .base import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""

    MEMBER = "member"
    CAPTAIN = "captain"
    COACH = "coach"
    ADMIN = "admin"


class User(Base):
    """User model for storing user information."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.MEMBER)
    team_id = Column(Integer, ForeignKey("teams.id"))
    is_approved = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="members")
    readmes = relationship("ReadMe", back_populates="author", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="author", cascade="all, delete-orphan")
    checklist_status = relationship("ChecklistStatus", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email}, role={self.role})>"

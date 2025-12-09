"""Team model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class Team(Base):
    """Team model for storing team information."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    team_id = Column(String(10), unique=True, nullable=False, index=True)  # Format: NN-NNNN
    division = Column(String(100), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Track creator
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    members = relationship("User", back_populates="team", foreign_keys="User.team_id", viewonly=True)
    readmes = relationship("ReadMe", back_populates="team", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="team", cascade="all, delete-orphan")
    creator = relationship("User", back_populates="created_teams", foreign_keys=[created_by_user_id])

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name}, team_id={self.team_id}, division={self.division})>"

"""Team model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .base import Base


class Team(Base):
    """Team model for storing team information."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    team_id = Column(String(10), unique=True, nullable=False, index=True)  # Format: NN-NNNN
    division = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    members = relationship("User", back_populates="team", cascade="all, delete-orphan")
    readmes = relationship("ReadMe", back_populates="team", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name}, team_id={self.team_id}, division={self.division})>"

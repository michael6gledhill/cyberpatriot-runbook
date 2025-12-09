"""README model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class ReadMe(Base):
    """Model for storing README documents."""

    __tablename__ = "readmes"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    os_type = Column(String(50), nullable=False)  # e.g., "Ubuntu 20.04", "Windows 10"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="readmes")
    author = relationship("User", back_populates="readmes")

    def __repr__(self):
        return f"<ReadMe(id={self.id}, title={self.title}, team_id={self.team_id})>"

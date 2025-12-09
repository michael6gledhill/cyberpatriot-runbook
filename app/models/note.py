"""Note model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class Note(Base):
    """Model for storing notes."""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    note_type = Column(String(50), nullable=False)  # general, point_note, password_change
    is_encrypted = Column(Boolean, default=False, nullable=False)
    encryption_key_salt = Column(String(255))  # Salt for encryption key derivation
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="notes")
    author = relationship("User", back_populates="notes")

    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title}, note_type={self.note_type})>"

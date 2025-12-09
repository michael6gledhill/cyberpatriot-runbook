"""Checklist models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from .base import Base


class ChecklistStatus(Base):
    """Model for tracking user's progress on checklist items."""

    __tablename__ = "checklist_status"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    checklist_item_id = Column(Integer, ForeignKey("checklist_items.id"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, completed, skipped
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="checklist_status")
    checklist_item = relationship("ChecklistItem", back_populates="status_records")

    def __repr__(self):
        return f"<ChecklistStatus(id={self.id}, user_id={self.user_id}, status={self.status})>"


class ChecklistItem(Base):
    """Model for individual checklist items."""

    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True)
    checklist_id = Column(Integer, ForeignKey("checklists.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    checklist = relationship("Checklist", back_populates="items")
    status_records = relationship("ChecklistStatus", back_populates="checklist_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChecklistItem(id={self.id}, checklist_id={self.checklist_id}, title={self.title})>"


class Checklist(Base):
    """Model for checklists."""

    __tablename__ = "checklists"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)  # e.g., "Ubuntu", "Windows", "Cisco"
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("ChecklistItem", back_populates="checklist", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Checklist(id={self.id}, title={self.title}, category={self.category})>"

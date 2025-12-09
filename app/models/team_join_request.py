"""Team join request model for managing coach/admin join requests."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from .base import Base


class JoinRequestStatus(str, enum.Enum):
    """Join request status enumeration."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class TeamJoinRequest(Base):
    """Model for tracking team join requests from coaches/admins."""

    __tablename__ = "team_join_requests"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    requester_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_creator_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(JoinRequestStatus), nullable=False, default=JoinRequestStatus.PENDING)
    message = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("Team", foreign_keys=[team_id])
    requester = relationship("User", foreign_keys=[requester_user_id])
    team_creator = relationship("User", foreign_keys=[team_creator_user_id])

    def __repr__(self):
        return f"<TeamJoinRequest(id={self.id}, team_id={self.team_id}, status={self.status})>"

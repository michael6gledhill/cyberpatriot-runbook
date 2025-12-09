"""Database access layer for models."""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.models.user import User, UserRole
from app.models.team import Team
from app.models.checklist import Checklist, ChecklistItem, ChecklistStatus
from app.models.readme import ReadMe
from app.models.note import Note
from app.models.audit_log import AuditLog
from app.models.team_join_request import TeamJoinRequest, JoinRequestStatus

from . import get_session


class UserRepository:
    """Repository for user-related database operations."""

    @staticmethod
    def create_user(
        name: str, email: str, password_hash: str, team_id: Optional[int] = None, role: UserRole = UserRole.MEMBER
    ) -> User:
        """Create a new user."""
        session = get_session()
        try:
            # Convert UserRole enum to its string value if needed
            role_value = role.value if isinstance(role, UserRole) else role
            
            user = User(
                name=name,
                email=email,
                password_hash=password_hash,
                team_id=team_id,
                role=role_value,
                is_approved=(role_value == UserRole.ADMIN.value),  # Admins auto-approved
            )
            session.add(user)
            session.commit()
            return user
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error creating user: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def get_user_by_email(email: str) -> User:
        """Get user by email."""
        session = get_session()
        try:
                user = session.query(User).options(joinedload(User.team)).filter(User.email == email).first()
            if user:
                session.expunge_all()
            return user
        finally:
            session.close()

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        """Get user by ID."""
        session = get_session()
        try:
                user = session.query(User).options(joinedload(User.team)).filter(User.id == user_id).first()
            if user:
                session.expunge_all()
            return user
        finally:
            session.close()

    @staticmethod
    def get_pending_users(team_id: Optional[int] = None) -> List[User]:
        """Get all pending approval users."""
        session = get_session()
        try:
            query = session.query(User).filter(User.is_approved == False)
            if team_id:
                query = query.filter(User.team_id == team_id)
            return query.all()
        finally:
            session.close()

    @staticmethod
    def approve_user(user_id: int) -> bool:
        """Approve a pending user."""
        session = get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.is_approved = True
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error approving user: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def reject_user(user_id: int) -> bool:
        """Reject a pending user."""
        session = get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error rejecting user: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def update_user_role(user_id: int, new_role: UserRole) -> bool:
        """Update user's role."""
        session = get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.role = new_role
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error updating user role: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def get_team_members(team_id: int) -> list:
        """Get all members of a team."""
        session = get_session()
        try:
            members = session.query(User).filter(User.team_id == team_id).all()
            return members
        finally:
            session.close()

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete a user from system."""
        session = get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error deleting user: {str(e)}")
        finally:
            session.close()


class TeamRepository:
    """Repository for team-related database operations."""

    @staticmethod
    def create_team(name: str, team_id: str, division: str, created_by_user_id: int) -> Team:
        """Create a new team."""
        session = get_session()
        try:
            team = Team(name=name, team_id=team_id, division=division, created_by_user_id=created_by_user_id)
            session.add(team)
            session.commit()
            return team
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error creating team: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def get_team_by_team_id(team_id: str) -> Team:
        """Get team by team ID (NN-NNNN format)."""
        session = get_session()
        try:
                team = session.query(Team).options(
                    joinedload(Team.members),
                    joinedload(Team.creator)
                ).filter(Team.team_id == team_id).first()
            if team:
                session.expunge_all()
            return team
        finally:
            session.close()

    @staticmethod
    def get_team_by_id(team_id: int) -> Team:
        """Get team by database ID."""
        session = get_session()
        try:
                team = session.query(Team).options(
                    joinedload(Team.members),
                    joinedload(Team.creator)
                ).filter(Team.id == team_id).first()
            if team:
                session.expunge_all()
            return team
        finally:
            session.close()

    @staticmethod
    def get_all_teams() -> list:
        """Get all teams."""
        session = get_session()
        try:
                teams = session.query(Team).options(
                    joinedload(Team.members),
                    joinedload(Team.creator)
                ).all()
            if teams:
                session.expunge_all()
            return teams
        finally:
            session.close()

    @staticmethod
    def update_team(team_db_id: int, name: Optional[str] = None, division: Optional[str] = None) -> bool:
        """Update team information."""
        session = get_session()
        try:
            team = session.query(Team).filter(Team.id == team_db_id).first()
            if team:
                if name:
                    team.name = name
                if division:
                    team.division = division
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error updating team: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def delete_team(team_db_id: int) -> bool:
        """Delete a team."""
        session = get_session()
        try:
            team = session.query(Team).filter(Team.id == team_db_id).first()
            if team:
                session.delete(team)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error deleting team: {str(e)}")
        finally:
            session.close()


class ChecklistRepository:
    """Repository for checklist-related database operations."""

    @staticmethod
    def create_checklist(title: str, description: str, category: str) -> Checklist:
        """Create a new checklist."""
        session = get_session()
        try:
            checklist = Checklist(title=title, description=description, category=category)
            session.add(checklist)
            session.commit()
            return checklist
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error creating checklist: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def get_checklist_by_id(checklist_id: int) -> Checklist:
        """Get checklist by ID."""
        session = get_session()
        try:
            checklist = session.query(Checklist).filter(Checklist.id == checklist_id).first()
            return checklist
        finally:
            session.close()

    @staticmethod
    def get_all_checklists() -> list:
        """Get all checklists."""
        session = get_session()
        try:
            checklists = session.query(Checklist).all()
            return checklists
        finally:
            session.close()

    @staticmethod
    def add_checklist_item(checklist_id: int, title: str, description: str, order: int) -> ChecklistItem:
        """Add an item to a checklist."""
        session = get_session()
        try:
            item = ChecklistItem(
                checklist_id=checklist_id, title=title, description=description, order=order
            )
            session.add(item)
            session.commit()
            return item
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error adding checklist item: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def get_checklist_status(user_id: int, checklist_item_id: int) -> ChecklistStatus:
        """Get user's status for a checklist item."""
        session = get_session()
        try:
            status = (
                session.query(ChecklistStatus)
                .filter(ChecklistStatus.user_id == user_id, ChecklistStatus.checklist_item_id == checklist_item_id)
                .first()
            )
            return status
        finally:
            session.close()

    @staticmethod
    def update_checklist_item_status(
        user_id: int, checklist_item_id: int, status: str, notes: Optional[str] = None
    ) -> ChecklistStatus:
        """Update user's status for a checklist item."""
        session = get_session()
        try:
            check_status = (
                session.query(ChecklistStatus)
                .filter(ChecklistStatus.user_id == user_id, ChecklistStatus.checklist_item_id == checklist_item_id)
                .first()
            )

            if check_status:
                check_status.status = status
                if notes:
                    check_status.notes = notes
            else:
                check_status = ChecklistStatus(
                    user_id=user_id, checklist_item_id=checklist_item_id, status=status, notes=notes
                )
                session.add(check_status)

            session.commit()
            return check_status
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error updating checklist status: {str(e)}")
        finally:
            session.close()


class ReadMeRepository:
    """Repository for README-related database operations."""

    @staticmethod
    def create_readme(team_id: int, user_id: int, title: str, os_type: str, content: str) -> ReadMe:
        """Create a new README."""
        session = get_session()
        try:
            readme = ReadMe(team_id=team_id, user_id=user_id, title=title, os_type=os_type, content=content)
            session.add(readme)
            session.commit()
            return readme
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error creating README: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def get_readme_by_id(readme_id: int) -> ReadMe:
        """Get README by ID."""
        session = get_session()
        try:
            readme = session.query(ReadMe).filter(ReadMe.id == readme_id).first()
            return readme
        finally:
            session.close()

    @staticmethod
    def get_team_readmes(team_id: int) -> list:
        """Get all READMEs for a team."""
        session = get_session()
        try:
            readmes = session.query(ReadMe).filter(ReadMe.team_id == team_id).all()
            return readmes
        finally:
            session.close()

    @staticmethod
    def update_readme(readme_id: int, title: Optional[str] = None, os_type: Optional[str] = None, content: Optional[str] = None) -> bool:
        """Update a README."""
        session = get_session()
        try:
            readme = session.query(ReadMe).filter(ReadMe.id == readme_id).first()
            if readme:
                if title:
                    readme.title = title
                if os_type:
                    readme.os_type = os_type
                if content:
                    readme.content = content
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error updating README: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def delete_readme(readme_id: int) -> bool:
        """Delete a README."""
        session = get_session()
        try:
            readme = session.query(ReadMe).filter(ReadMe.id == readme_id).first()
            if readme:
                session.delete(readme)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error deleting README: {str(e)}")
        finally:
            session.close()


class NoteRepository:
    """Repository for note-related database operations."""

    @staticmethod
    def create_note(
        team_id: int, user_id: int, title: str, content: str, note_type: str = "general", is_encrypted: bool = False
    ) -> Note:
        """Create a new note."""
        session = get_session()
        try:
            note = Note(
                team_id=team_id,
                user_id=user_id,
                title=title,
                content=content,
                note_type=note_type,
                is_encrypted=is_encrypted,
            )
            session.add(note)
            session.commit()
            return note
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error creating note: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def get_note_by_id(note_id: int) -> Note:
        """Get note by ID."""
        session = get_session()
        try:
            note = session.query(Note).filter(Note.id == note_id).first()
            return note
        finally:
            session.close()

    @staticmethod
    def get_team_notes(team_id: int) -> list:
        """Get all notes for a team."""
        session = get_session()
        try:
            notes = session.query(Note).filter(Note.team_id == team_id).all()
            return notes
        finally:
            session.close()

    @staticmethod
    def update_note(note_id: int, title: Optional[str] = None, content: Optional[str] = None) -> bool:
        """Update a note."""
        session = get_session()
        try:
            note = session.query(Note).filter(Note.id == note_id).first()
            if note:
                if title:
                    note.title = title
                if content:
                    note.content = content
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error updating note: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def delete_note(note_id: int) -> bool:
        """Delete a note."""
        session = get_session()
        try:
            note = session.query(Note).filter(Note.id == note_id).first()
            if note:
                session.delete(note)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error deleting note: {str(e)}")
        finally:
            session.close()


class AuditLogRepository:
    """Repository for audit log operations."""

    @staticmethod
    def log_action(user_id: int, action: str, resource_type: str, resource_id: Optional[int] = None, description: Optional[str] = None):
        """Log a user action."""
        session = get_session()
        try:
            log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=description,
            )
            session.add(log)
            session.commit()
            return log
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error logging action: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def get_audit_logs(limit: int = 100) -> list:
        """Get recent audit logs."""
        session = get_session()
        try:
            logs = (
                session.query(AuditLog)
                .options(joinedload(AuditLog.user))
                .order_by(AuditLog.created_at.desc())
                .limit(limit)
                .all()
            )
            if logs:
                session.expunge_all()
            return logs
        finally:
            session.close()


class TeamJoinRequestRepository:
    """Repository for team join request operations."""

    @staticmethod
    def create_request(
        team_id: int, requester_user_id: int, team_creator_user_id: int, message: Optional[str] = None
    ) -> TeamJoinRequest:
        """Create a new team join request."""
        session = get_session()
        try:
            request = TeamJoinRequest(
                team_id=team_id,
                requester_user_id=requester_user_id,
                team_creator_user_id=team_creator_user_id,
                status=JoinRequestStatus.PENDING,
                message=message,
            )
            session.add(request)
            session.commit()
            return request
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error creating team join request: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def get_request_by_id(request_id: int) -> Optional[TeamJoinRequest]:
        """Get team join request by ID."""
        session = get_session()
        try:
            request = session.query(TeamJoinRequest).filter(TeamJoinRequest.id == request_id).first()
            return request
        finally:
            session.close()

    @staticmethod
    def get_pending_requests_for_team(team_id: int) -> List[TeamJoinRequest]:
        """Get all pending join requests for a team."""
        session = get_session()
        try:
            requests = (
                session.query(TeamJoinRequest)
                .filter(TeamJoinRequest.team_id == team_id, TeamJoinRequest.status == JoinRequestStatus.PENDING)
                .all()
            )
            return requests
        finally:
            session.close()

    @staticmethod
    def get_pending_requests_for_user(requester_user_id: int) -> List[TeamJoinRequest]:
        """Get all pending join requests made by a user."""
        session = get_session()
        try:
            requests = (
                session.query(TeamJoinRequest)
                .filter(
                    TeamJoinRequest.requester_user_id == requester_user_id,
                    TeamJoinRequest.status == JoinRequestStatus.PENDING,
                )
                .all()
            )
            return requests
        finally:
            session.close()

    @staticmethod
    def check_request_exists(team_id: int, requester_user_id: int) -> Optional[TeamJoinRequest]:
        """Check if a join request already exists for this team/user."""
        session = get_session()
        try:
            request = (
                session.query(TeamJoinRequest)
                .filter(
                    TeamJoinRequest.team_id == team_id, TeamJoinRequest.requester_user_id == requester_user_id
                )
                .first()
            )
            return request
        finally:
            session.close()

    @staticmethod
    def approve_request(request_id: int) -> bool:
        """Approve a join request."""
        session = get_session()
        try:
            request = session.query(TeamJoinRequest).filter(TeamJoinRequest.id == request_id).first()
            if request:
                request.status = JoinRequestStatus.APPROVED
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error approving join request: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def reject_request(request_id: int) -> bool:
        """Reject a join request."""
        session = get_session()
        try:
            request = session.query(TeamJoinRequest).filter(TeamJoinRequest.id == request_id).first()
            if request:
                request.status = JoinRequestStatus.REJECTED
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error rejecting join request: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def delete_request(request_id: int) -> bool:
        """Delete a join request."""
        session = get_session()
        try:
            request = session.query(TeamJoinRequest).filter(TeamJoinRequest.id == request_id).first()
            if request:
                session.delete(request)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error deleting join request: {str(e)}")
        finally:
            session.close()

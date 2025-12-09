"""Authentication and authorization controllers."""

from app.database.repositories import UserRepository, TeamRepository
from app.security import PasswordManager
from app.models.user import UserRole


class AuthController:
    """Controller for authentication operations."""

    @staticmethod
    def login(email: str, password: str) -> dict:
        """Authenticate user with email and password.

        Args:
            email: User's email
            password: User's password

        Returns:
            User data dict if successful, None otherwise

        Raises:
            ValueError: If credentials are invalid
        """
        user = UserRepository.get_user_by_email(email)

        if not user:
            raise ValueError("User not found")

        if not PasswordManager.verify_password(password, user.password_hash):
            raise ValueError("Invalid password")

        if not user.is_active:
            raise ValueError("Account is inactive")

        # Check approval status for non-admins
        if user.role != UserRole.ADMIN and not user.is_approved:
            raise ValueError("Account pending approval")

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
            "team_id": user.team_id,
            "is_approved": user.is_approved,
        }

    @staticmethod
    def signup(
        name: str, email: str, password: str, team_id_str: str, requested_role: str
    ) -> dict:
        """Register a new user.

        Args:
            name: User's full name
            email: User's email
            password: User's password
            team_id_str: Team ID in format NN-NNNN
            requested_role: Requested role (member, captain, coach)

        Returns:
            New user data dict

        Raises:
            ValueError: If signup validation fails
        """
        # Validate email not already in use
        existing = UserRepository.get_user_by_email(email)
        if existing:
            raise ValueError("Email already in use")

        # Validate password strength
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        # Validate team exists
        team = TeamRepository.get_team_by_team_id(team_id_str)
        if not team:
            raise ValueError(f"Team '{team_id_str}' not found")

        # Hash password
        password_hash = PasswordManager.hash_password(password)

        # Create user (pending approval)
        user = UserRepository.create_user(
            name=name,
            email=email,
            password_hash=password_hash,
            team_id=team.id,
            role=requested_role,
        )

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
            "team_id": user.team_id,
            "is_approved": user.is_approved,
        }


class AdminController:
    """Controller for admin operations."""

    @staticmethod
    def approve_user(user_id: int, admin_id: int) -> bool:
        """Approve a pending user.

        Args:
            user_id: User to approve
            admin_id: Admin performing action

        Returns:
            True if successful
        """
        from app.database.repositories import AuditLogRepository

        if UserRepository.approve_user(user_id):
            AuditLogRepository.log_action(admin_id, "approve_user", "user", user_id)
            return True
        return False

    @staticmethod
    def reject_user(user_id: int, admin_id: int) -> bool:
        """Reject and remove a pending user.

        Args:
            user_id: User to reject
            admin_id: Admin performing action

        Returns:
            True if successful
        """
        from app.database.repositories import AuditLogRepository

        if UserRepository.reject_user(user_id):
            AuditLogRepository.log_action(admin_id, "reject_user", "user", user_id)
            return True
        return False

    @staticmethod
    def change_user_role(user_id: int, new_role: str, admin_id: int) -> bool:
        """Change a user's role.

        Args:
            user_id: User to update
            new_role: New role
            admin_id: Admin performing action

        Returns:
            True if successful
        """
        from app.database.repositories import AuditLogRepository

        if UserRepository.update_user_role(user_id, new_role):
            AuditLogRepository.log_action(
                admin_id, "change_role", "user", user_id, f"Changed to {new_role}"
            )
            return True
        return False

    @staticmethod
    def remove_user(user_id: int, admin_id: int) -> bool:
        """Remove a user from the system.

        Args:
            user_id: User to remove
            admin_id: Admin performing action

        Returns:
            True if successful
        """
        from app.database.repositories import AuditLogRepository

        if UserRepository.delete_user(user_id):
            AuditLogRepository.log_action(admin_id, "remove_user", "user", user_id)
            return True
        return False

    @staticmethod
    def create_team(name: str, team_id: str, division: str, admin_id: int) -> dict:
        """Create a new team.

        Args:
            name: Team name
            team_id: Team ID in format NN-NNNN
            division: Team division
            admin_id: Admin performing action

        Returns:
            New team data dict
        """
        from app.database.repositories import AuditLogRepository

        team = TeamRepository.create_team(name, team_id, division, admin_id)
        AuditLogRepository.log_action(admin_id, "create_team", "team", team.id)

        return {
            "id": team.id,
            "name": team.name,
            "team_id": team.team_id,
            "division": team.division,
        }

    @staticmethod
    def update_team(team_id: int, name: str, division: str, admin_id: int) -> bool:
        """Update team information.

        Args:
            team_id: Team to update
            name: New team name
            division: New division
            admin_id: Admin performing action

        Returns:
            True if successful
        """
        from app.database.repositories import AuditLogRepository

        if TeamRepository.update_team(team_id, name, division):
            AuditLogRepository.log_action(admin_id, "update_team", "team", team_id)
            return True
        return False

    @staticmethod
    def delete_team(team_id: int, admin_id: int) -> bool:
        """Delete a team.

        Args:
            team_id: Team to delete
            admin_id: Admin performing action

        Returns:
            True if successful
        """
        from app.database.repositories import AuditLogRepository

        if TeamRepository.delete_team(team_id):
            AuditLogRepository.log_action(admin_id, "delete_team", "team", team_id)
            return True
        return False

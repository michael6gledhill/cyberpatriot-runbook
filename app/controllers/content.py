"""Controllers for checklist, README, and note operations."""

from app.database.repositories import (
    ChecklistRepository,
    ReadMeRepository,
    NoteRepository,
    AuditLogRepository,
)
from app.security import EncryptionManager


class ChecklistController:
    """Controller for checklist operations."""

    @staticmethod
    def get_user_checklist_progress(user_id: int, checklist_id: int) -> dict:
        """Get user's progress on a checklist.

        Args:
            user_id: User ID
            checklist_id: Checklist ID

        Returns:
            Progress data dict
        """
        checklist = ChecklistRepository.get_checklist_by_id(checklist_id)

        if not checklist:
            return None

        completed = 0
        skipped = 0
        pending = 0

        for item in checklist.items:
            status = ChecklistRepository.get_checklist_status(user_id, item.id)
            if status:
                if status.status == "completed":
                    completed += 1
                elif status.status == "skipped":
                    skipped += 1
                else:
                    pending += 1
            else:
                pending += 1

        return {
            "checklist_id": checklist_id,
            "title": checklist.title,
            "total_items": len(checklist.items),
            "completed": completed,
            "skipped": skipped,
            "pending": pending,
            "progress_percent": (
                (completed + skipped) / len(checklist.items) * 100 if checklist.items else 0
            ),
        }

    @staticmethod
    def update_item_status(user_id: int, item_id: int, status: str, notes: str = None) -> bool:
        """Update user's status for a checklist item.

        Args:
            user_id: User ID
            item_id: Checklist item ID
            status: New status (pending, completed, skipped)
            notes: Optional notes

        Returns:
            True if successful
        """
        ChecklistRepository.update_checklist_item_status(user_id, item_id, status, notes)
        AuditLogRepository.log_action(
            user_id, "update_checklist", "checklist_item", item_id, f"Status: {status}"
        )
        return True


class ReadMeController:
    """Controller for README operations."""

    @staticmethod
    def create_readme(
        team_id: int, user_id: int, title: str, os_type: str, content: str
    ) -> dict:
        """Create a new README.

        Args:
            team_id: Team ID
            user_id: User creating README
            title: README title
            os_type: OS type (e.g., "Ubuntu 20.04")
            content: README content

        Returns:
            New README data dict
        """
        readme = ReadMeRepository.create_readme(team_id, user_id, title, os_type, content)
        AuditLogRepository.log_action(user_id, "create_readme", "readme", readme.id)

        return {
            "id": readme.id,
            "title": readme.title,
            "os_type": readme.os_type,
            "team_id": readme.team_id,
        }

    @staticmethod
    def update_readme(
        readme_id: int, user_id: int, title: str = None, os_type: str = None, content: str = None
    ) -> bool:
        """Update a README.

        Args:
            readme_id: README to update
            user_id: User updating
            title: New title
            os_type: New OS type
            content: New content

        Returns:
            True if successful
        """
        if ReadMeRepository.update_readme(readme_id, title, os_type, content):
            AuditLogRepository.log_action(user_id, "update_readme", "readme", readme_id)
            return True
        return False

    @staticmethod
    def delete_readme(readme_id: int, user_id: int) -> bool:
        """Delete a README.

        Args:
            readme_id: README to delete
            user_id: User deleting

        Returns:
            True if successful
        """
        if ReadMeRepository.delete_readme(readme_id):
            AuditLogRepository.log_action(user_id, "delete_readme", "readme", readme_id)
            return True
        return False


class NoteController:
    """Controller for note operations."""

    @staticmethod
    def create_note(
        team_id: int,
        user_id: int,
        title: str,
        content: str,
        note_type: str = "general",
        encrypt: bool = False,
        password: str = None,
    ) -> dict:
        """Create a new note.

        Args:
            team_id: Team ID
            user_id: User creating note
            title: Note title
            content: Note content
            note_type: Type of note
            encrypt: Whether to encrypt
            password: Password for encryption

        Returns:
            New note data dict
        """
        if encrypt and password:
            encrypted_content, salt = EncryptionManager.encrypt_note(content, password)
            note = NoteRepository.create_note(
                team_id, user_id, title, encrypted_content, note_type, is_encrypted=True
            )
            # Store salt separately in the database
            note.encryption_key_salt = salt
        else:
            note = NoteRepository.create_note(
                team_id, user_id, title, content, note_type, is_encrypted=False
            )

        AuditLogRepository.log_action(user_id, "create_note", "note", note.id)

        return {
            "id": note.id,
            "title": note.title,
            "note_type": note.note_type,
            "is_encrypted": note.is_encrypted,
        }

    @staticmethod
    def update_note(note_id: int, user_id: int, title: str = None, content: str = None) -> bool:
        """Update a note.

        Args:
            note_id: Note to update
            user_id: User updating
            title: New title
            content: New content

        Returns:
            True if successful
        """
        if NoteRepository.update_note(note_id, title, content):
            AuditLogRepository.log_action(user_id, "update_note", "note", note_id)
            return True
        return False

    @staticmethod
    def delete_note(note_id: int, user_id: int) -> bool:
        """Delete a note.

        Args:
            note_id: Note to delete
            user_id: User deleting

        Returns:
            True if successful
        """
        if NoteRepository.delete_note(note_id):
            AuditLogRepository.log_action(user_id, "delete_note", "note", note_id)
            return True
        return False

    @staticmethod
    def decrypt_note(note_id: int, password: str) -> str:
        """Decrypt an encrypted note.

        Args:
            note_id: Note to decrypt
            password: Password for decryption

        Returns:
            Decrypted content

        Raises:
            ValueError: If decryption fails
        """
        note = NoteRepository.get_note_by_id(note_id)

        if not note or not note.is_encrypted:
            raise ValueError("Note not found or not encrypted")

        return EncryptionManager.decrypt_note(note.content, password, note.encryption_key_salt)

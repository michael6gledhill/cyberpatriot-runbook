"""Security utilities for password hashing and encryption."""

import bcrypt
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class PasswordManager:
    """Manages password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash.

        Args:
            password: Plain text password to verify
            password_hash: Hashed password to check against

        Returns:
            True if password matches hash, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except Exception:
            return False


class EncryptionManager:
    """Manages encryption and decryption of sensitive data."""

    @staticmethod
    def generate_key(password: str, salt: bytes = None) -> tuple:
        """Generate an encryption key from a password.

        Args:
            password: Password to derive key from
            salt: Optional salt bytes. If None, generates new salt.

        Returns:
            Tuple of (encryption_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
        return key, salt

    @staticmethod
    def encrypt_text(text: str, encryption_key: bytes) -> str:
        """Encrypt text using Fernet symmetric encryption.

        Args:
            text: Plain text to encrypt
            encryption_key: Encryption key (from generate_key)

        Returns:
            Encrypted text as string
        """
        cipher = Fernet(encryption_key)
        encrypted = cipher.encrypt(text.encode("utf-8"))
        return encrypted.decode("utf-8")

    @staticmethod
    def decrypt_text(encrypted_text: str, encryption_key: bytes) -> str:
        """Decrypt text using Fernet symmetric encryption.

        Args:
            encrypted_text: Encrypted text to decrypt
            encryption_key: Encryption key (from generate_key)

        Returns:
            Decrypted plain text
        """
        try:
            cipher = Fernet(encryption_key)
            decrypted = cipher.decrypt(encrypted_text.encode("utf-8"))
            return decrypted.decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to decrypt text: {str(e)}")

    @staticmethod
    def encrypt_note(note_content: str, user_password: str) -> tuple:
        """Encrypt a note with user's password.

        Args:
            note_content: Content to encrypt
            user_password: User's password to derive encryption key

        Returns:
            Tuple of (encrypted_content, salt_string)
        """
        key, salt = EncryptionManager.generate_key(user_password)
        encrypted = EncryptionManager.encrypt_text(note_content, key)
        salt_string = base64.b64encode(salt).decode("utf-8")
        return encrypted, salt_string

    @staticmethod
    def decrypt_note(encrypted_content: str, user_password: str, salt_string: str) -> str:
        """Decrypt a note with user's password.

        Args:
            encrypted_content: Encrypted note content
            user_password: User's password
            salt_string: Salt string (base64 encoded)

        Returns:
            Decrypted note content
        """
        salt = base64.b64decode(salt_string.encode("utf-8"))
        key, _ = EncryptionManager.generate_key(user_password, salt)
        return EncryptionManager.decrypt_text(encrypted_content, key)

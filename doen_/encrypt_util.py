import os
import zipfile
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional


class EncrytionUtils:
    """
    A utility class for handling encryption, decryption, file operations, and password strength checking.
    """

    @staticmethod
    def password_strength_checker(password: str) -> bool:
        """Check the strength of a password.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password is strong, False otherwise.

        Examples:
            >>> password_strength_checker("Weakpass")
            False
            >>> password_strength_checker("Strongpass1")
            True
        """
        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password):
            return False
        return True

    @staticmethod
    def generate_encryption_key(password: Optional[str] = None, salt: Optional[bytes] = None) -> str:
        """Generate an encryption key from a password and salt.

        Args:
            password (Optional[str]): The password to derive the key from. If None, a random key is generated.
            salt (Optional[bytes]): A salt for the key derivation. If None, a random salt is used.

        Returns:
            str: The generated encryption key as a URL-safe base64-encoded string.

        Raises:
            ValueError: If the password is too weak.

        Examples:
            >>> key = generate_encryption_key("Strongpass1")
            >>> isinstance(key, str)
            True
        """
        if password:
            if not EncrytionUtils.password_strength_checker(password):
                raise ValueError("Password is too weak.")
            if not salt:
                salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode())
            return urlsafe_b64encode(key).decode()
        else:
            return Fernet.generate_key().decode()

    @staticmethod
    def generate_encryption_key(password: str = None, salt: bytes = None) -> str:
        """
        Generate an encryption key.

        Args:
            password (str, optional): The password to use for the key. If not provided, a random key is generated.
            salt (bytes, optional): The salt to use for the key. If not provided, a random salt is generated.

        Returns:
            str: The generated encryption key.

        Example:
            >>> generate_encryption_key(password="test_password")
            'esvCExTuhddRb8kSobU_gnNRYObyTRTI2LJF4nYai5I='
        """
        if password:
            if not salt:
                salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode())
            return urlsafe_b64encode(key).decode()
        else:
            return Fernet.generate_key().decode()

    @staticmethod
    def encrypt(data: str, key: str) -> str:
        """
        Encrypt the provided data using the provided key.

        Args:
            data (str): The data to encrypt.
            key (str): The encryption key.

        Returns:
            str: The encrypted data.

        Example:
            >>> encrypt("This is some test data.", "esvCExTuhddRb8kSobU_gnNRYObyTRTI2LJF4nYai5I=")
            'gAAAAABloX9m_S_G1VUtbfGUDB7ooHJNt8sPiSCwnp1ehe6dExvMEqtw_ua2ELk_uUbLoB6a1XkbKLOkM4UBvwmk6sMoY-yNvE-Lv-w-VNnfzf89zH82rgI='
        """
        fernet = Fernet(key.encode())
        return fernet.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt(data: str, key: str) -> str:
        """
        Decrypt the provided data using the provided key.

        Args:
            data (str): The data to decrypt.
            key (str): The encryption key.

        Returns:
            str: The decrypted data.

        Example:
            >>> decrypt('gAAAAABloX9m_S_G1VUtbfGUDB7ooHJNt8sPiSCwnp1ehe6dExvMEqtw_ua2ELk_uUbLoB6a1XkbKLOkM4UBvwmk6sMoY-yNvE-Lv-w-VNnfzf89zH82rgI=', "esvCExTuhddRb8kSobU_gnNRYObyTRTI2LJF4nYai5I=")
            'This is some test data.'
        """
        fernet = Fernet(key.encode())
        return fernet.decrypt(data.encode()).decode()

    @staticmethod
    def encrypt_file(file_path: str, key: str, output_path: str = None):
        """
        Encrypt a file.

        Args:
            file_path (str): The path of the file to encrypt.
            key (str): The encryption key.
            output_path (str, optional): The path to save the encrypted file. If not provided, '.enc' is appended to the input file path.

        Example:
            >>> encrypt_file("test_file.txt", "esvCExTuhddRb8kSobU_gnNRYObyTRTI2LJF4nYai5I=")
        """
        if not output_path:
            output_path = file_path + '.enc'
        with open(file_path, 'rb') as file_to_encrypt:
            encrypted_data = EncrytionUtils.encrypt(file_to_encrypt.read().decode(), key)
        with open(output_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data.encode())

    @staticmethod
    def decrypt_file(encrypted_file_path: str, key: str, output_path: str = None):
        """
        Decrypt a file.

        Args:
            encrypted_file_path (str): The path of the file to decrypt.
            key (str): The encryption key.
            output_path (str, optional): The path to save the decrypted file. If not provided, '.enc' is removed from the input file path.

        Example:
            >>> decrypt_file("test_file.txt.enc", "esvCExTuhddRb8kSobU_gnNRYObyTRTI2LJF4nYai5I=")
        """
        if not output_path:
            output_path = encrypted_file_path.replace('.enc', '')
        with open(encrypted_file_path, 'rb') as encrypted_file:
            decrypted_data = EncrytionUtils.decrypt(encrypted_file.read().decode(), key)
        with open(output_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data.encode())

    @staticmethod
    def is_encrypted(file_path: str, key: str) -> bool:
        """
        Check if a file is encrypted.

        Args:
            file_path (str): The path of the file to check.
            key (str): The encryption key.

        Returns:
            bool: True if the file is encrypted, False otherwise.

        Example:
            >>> is_encrypted("test_file.txt.enc", "esvCExTuhddRb8kSobU_gnNRYObyTRTI2LJF4nYai5I=")
            True
        """
        try:
            EncrytionUtils.decrypt_file(file_path, key, "temp_decrypted_file")
            os.remove("temp_decrypted_file")
            return True
        except InvalidToken:
            return False

    @staticmethod
    def decompress_file(file_path: str, output_path: str = None):
        """
        Decompress a file.

        Args:
            file_path (str): The path of the file to decompress.
            output_path (str, optional): The path to save the decompressed file. If not provided, the file is decompressed in the same directory.

        Example:
            >>> decompress_file("test_file.txt.zip")
        """
        if not output_path:
            output_path = os.path.dirname(file_path)
        with zipfile.ZipFile(file_path, 'r') as zipf:
            zipf.extractall(output_path)

    @staticmethod
    def compress_file(file_path: str, output_path: str = None):
        """
        Compress a file.

        Args:
            file_path (str): The path of the file to compress.
            output_path (str, optional): The path to save the compressed file. If not provided, '.zip' is appended to the input file path.

        Example:
            >>> compress_file("test_file.txt")
        """
        if not output_path:
            output_path = file_path + '.zip'
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path)

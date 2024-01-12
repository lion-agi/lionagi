# Standard library imports
import os
from base64 import urlsafe_b64encode
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


def generate_encryption_key(password: str = None, salt: bytes = None) -> str:
    """
    Generates a key for encryption, optionally based on a password.

    Args:
        password (str, optional): The password to use for key derivation. If None, a random key is generated.
        salt (bytes, optional): A salt for key derivation. Ignored if password is None. Randomly generated if not provided.

    Returns:
        str: The generated encryption key.
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

def encrypt(data: str, key: str) -> str:
    """
    Encrypts data using the provided key.

    Args:
        data (str): The data to be encrypted.
        key (str): The encryption key.

    Returns:
        str: The encrypted data.
    """
    fernet = Fernet(key.encode())
    return fernet.encrypt(data.encode()).decode()

def decrypt(data: str, key: str) -> str:
    """
    Decrypts data using the provided key.

    Args:
        data (str): The data to be decrypted.
        key (str): The decryption key.

    Returns:
        str: The decrypted data.
    """
    fernet = Fernet(key.encode())
    return fernet.decrypt(data.encode()).decode()

def encrypt_file(file_path: str, key: str, output_path: str = None):
    """
    Encrypts a file using the provided key.

    Args:
        file_path (str): Path to the file to be encrypted.
        key (str): The encryption key.
        output_path (str, optional): Path to save the encrypted file. If None, appends '.enc' to the original file name.

    """
    if not output_path:
        output_path = file_path + '.enc'
    with open(file_path, 'rb') as file_to_encrypt:
        encrypted_data = encrypt(file_to_encrypt.read(), key)
    with open(output_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)

def decrypt_file(encrypted_file_path: str, key: str, output_path: str = None):
    """
    Decrypts a file using the provided key.

    Args:
        encrypted_file_path (str): Path to the encrypted file.
        key (str): The decryption key.
        output_path (str, optional): Path to save the decrypted file. If None, removes '.enc' from the original file name.

    """
    if not output_path:
        output_path = encrypted_file_path.replace('.enc', '')
    with open(encrypted_file_path, 'rb') as encrypted_file:
        decrypted_data = decrypt(encrypted_file.read(), key)
    with open(output_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)

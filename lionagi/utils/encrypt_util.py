# this module has no internal dependency 
from cryptography.fernet import Fernet

def generate_encryption_key() -> str:
    """Generates a key for encryption."""
    return Fernet.generate_key().decode()

def encrypt(data: str, key: str) -> str:
    """Encrypts data using the provided key."""
    fernet = Fernet(key.encode())
    return fernet.encrypt(data.encode()).decode()

def decrypt(data: str, key: str) -> str:
    """Decrypts data using the provided key."""
    fernet = Fernet(key.encode())
    return fernet.decrypt(data.encode()).decode()

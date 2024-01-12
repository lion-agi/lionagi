# filename: enhanced_encryption.py

import os
import zipfile
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

def generate_encryption_key(password: str = None, salt: bytes = None) -> str:
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
    fernet = Fernet(key.encode())
    return fernet.encrypt(data.encode()).decode()

def decrypt(data: str, key: str) -> str:
    fernet = Fernet(key.encode())
    return fernet.decrypt(data.encode()).decode()

def encrypt_file(file_path: str, key: str, output_path: str = None):
    if not output_path:
        output_path = file_path + '.enc'
    with open(file_path, 'rb') as file_to_encrypt:
        encrypted_data = encrypt(file_to_encrypt.read().decode(), key)
    with open(output_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data.encode())

def decrypt_file(encrypted_file_path: str, key: str, output_path: str = None):
    if not output_path:
        output_path = encrypted_file_path.replace('.enc', '')
    with open(encrypted_file_path, 'rb') as encrypted_file:
        decrypted_data = decrypt(encrypted_file.read().decode(), key)
    with open(output_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data.encode())

def is_encrypted(file_path: str, key: str) -> bool:
    try:
        decrypt_file(file_path, key, "temp_decrypted_file")
        os.remove("temp_decrypted_file")
        return True
    except InvalidToken:
        return False

def compress_file(file_path: str, output_path: str = None):
    if not output_path:
        output_path = file_path + '.zip'
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path)

def decompress_file(file_path: str, output_path: str = None):
    if not output_path:
        output_path = os.path.dirname(file_path)
    with zipfile.ZipFile(file_path, 'r') as zipf:
        zipf.extractall(output_path)

# Test the functions
key = generate_encryption_key(password="test_password")
print("Generated key:", key)

data = "This is some test data."
encrypted_data = encrypt(data, key)
print("Encrypted data:", encrypted_data)

decrypted_data = decrypt(encrypted_data, key)
print("Decrypted data:", decrypted_data)

# Create a test file
with open("test_file.txt", "w") as f:
    f.write(data)

# Encrypt the file
encrypt_file("test_file.txt", key)

# Check if the file is encrypted
print("Is the file encrypted?", is_encrypted("test_file.txt.enc", key))

# Decrypt the file
decrypt_file("test_file.txt.enc", key)

# Check if the decrypted file is the same as the original
with open("test_file.txt", "r") as f:
    original_data = f.read()

with open("test_file.txt", "r") as f:
    decrypted_file_data = f.read()

print("Original file data:", original_data)
print("Decrypted file data:", decrypted_file_data)

# Compress the file
compress_file("test_file.txt")

# Decompress the file
decompress_file("test_file.txt.zip")
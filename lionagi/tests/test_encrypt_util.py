import unittest
from cryptography.fernet import Fernet

# Assuming the Python module with the above functions is named 'encryption_utils'
from lionagi.utils.encrypt_util import generate_encryption_key, encrypt, decrypt

class TestEncryptionUtils(unittest.TestCase):

    def test_generate_encryption_key(self):
        key = generate_encryption_key()
        self.assertIsInstance(key, str)
        self.assertEqual(len(key), 44)  # Fernet keys are 44 bytes long in URL-safe base64 encoding

    def test_encrypt_decrypt(self):
        key = generate_encryption_key()
        original_data = "Test data for encryption"
        encrypted_data = encrypt(original_data, key)
        decrypted_data = decrypt(encrypted_data, key)

        self.assertNotEqual(encrypted_data, original_data)
        self.assertEqual(decrypted_data, original_data)

    def test_invalid_key(self):
        key = generate_encryption_key()
        wrong_key = Fernet.generate_key().decode()
        original_data = "Test data for encryption"
        encrypted_data = encrypt(original_data, key)

        with self.assertRaises(Exception):
            decrypt(encrypted_data, wrong_key)

if __name__ == '__main__':
    unittest.main()
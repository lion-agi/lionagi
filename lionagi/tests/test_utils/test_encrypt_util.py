import unittest
import os
import tempfile
import zipfile
import hashlib
from cryptography.fernet import InvalidToken
from lionagi.utils.encrypt_util import EncrytionUtil


class TestPasswordStrengthChecker(unittest.TestCase):

    def test_short_passwords(self):
        self.assertFalse(EncrytionUtil.password_strength_checker("Short1"))
        self.assertFalse(EncrytionUtil.password_strength_checker("A1"))

    def test_passwords_without_digits(self):
        self.assertFalse(EncrytionUtil.password_strength_checker("NoDigitsHere"))
        self.assertFalse(EncrytionUtil.password_strength_checker("Onlyletters!"))

    def test_passwords_without_uppercase(self):
        self.assertFalse(EncrytionUtil.password_strength_checker("alllowercase1"))
        self.assertFalse(EncrytionUtil.password_strength_checker("nouppercase1!"))

    def test_strong_passwords(self):
        self.assertTrue(EncrytionUtil.password_strength_checker("ValidPass1"))
        self.assertTrue(EncrytionUtil.password_strength_checker("AnotherGood1"))


class TestGenerateEncryptionKey(unittest.TestCase):

    def setUp(self):
        # Strong password and predefined salt for testing
        self.strong_password = "StrongPass1"
        self.salt = b'0123456789abcdef'

    def test_with_strong_password_and_provided_salt(self):
        key = EncrytionUtil.generate_encryption_key(password=self.strong_password, salt=self.salt)
        self.assertIsInstance(key, str)

    def test_with_strong_password_and_no_salt(self):
        key = EncrytionUtil.generate_encryption_key(password=self.strong_password)
        self.assertIsInstance(key, str)

    def test_with_weak_password(self):
        with self.assertRaises(ValueError):
            EncrytionUtil.generate_encryption_key(password="weak")

    def test_with_no_password(self):
        key = EncrytionUtil.generate_encryption_key()
        self.assertIsInstance(key, str)
        self.assertEqual(len(key), 44)  # Typical length of a Fernet key


class TestEncrypt(unittest.TestCase):

    def setUp(self):
        self.valid_key = EncrytionUtil.generate_encryption_key("StrongPass1")
        self.invalid_key = "invalidkey"
        self.test_data = "This is a test string."

    def test_valid_encryption(self):
        encrypted_data = EncrytionUtil.encrypt(self.test_data, self.valid_key)
        self.assertIsInstance(encrypted_data, str)
        self.assertNotEqual(encrypted_data, self.test_data)

    def test_with_invalid_key(self):
        with self.assertRaises(Exception):
            EncrytionUtil.encrypt(self.test_data, self.invalid_key)

    def test_with_non_string_data(self):
        with self.assertRaises(AttributeError):  # or whichever error is appropriate
            EncrytionUtil.encrypt(12345, self.valid_key)

    def test_with_empty_string(self):
        encrypted_data = EncrytionUtil.encrypt("", self.valid_key)
        self.assertIsInstance(encrypted_data, str)
        self.assertNotEqual(encrypted_data, "")


class TestDecrypt(unittest.TestCase):

    def setUp(self):
        self.valid_key = EncrytionUtil.generate_encryption_key("StrongPass1")
        self.invalid_key = "invalidkey"
        self.test_data = "This is a test string."
        self.encrypted_data = EncrytionUtil.encrypt(self.test_data, self.valid_key)

    def test_valid_decryption(self):
        decrypted_data = EncrytionUtil.decrypt(self.encrypted_data, self.valid_key)
        self.assertIsInstance(decrypted_data, str)
        self.assertEqual(decrypted_data, self.test_data)

    def test_decryption_with_invalid_key(self):
        with self.assertRaises(ValueError):
            EncrytionUtil.decrypt(self.encrypted_data, self.invalid_key)

    def test_with_non_string_data(self):
        with self.assertRaises(AttributeError):
            EncrytionUtil.decrypt(12345, self.valid_key)

    def test_decryption_of_non_encrypted_string(self):
        with self.assertRaises(InvalidToken):
            EncrytionUtil.decrypt("plain text", self.valid_key)


class TestEncryptFile(unittest.TestCase):

    def setUp(self):
        self.valid_key = EncrytionUtil.generate_encryption_key("StrongPass1")
        # Create a temporary file with some test data
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b"This is a test file.")
        self.temp_file.close()

    def tearDown(self):
        # Cleanup: Remove temporary files
        os.remove(self.temp_file.name)
        if os.path.exists(self.temp_file.name + '.enc'):
            os.remove(self.temp_file.name + '.enc')

    def test_encrypting_valid_file(self):
        EncrytionUtil.encrypt_file(self.temp_file.name, self.valid_key)
        self.assertTrue(os.path.exists(self.temp_file.name + '.enc'))

    def test_with_non_existent_file_path(self):
        with self.assertRaises(FileNotFoundError):
            EncrytionUtil.encrypt_file("non_existent_file.txt", self.valid_key)


class TestDecryptFile(unittest.TestCase):

    def setUp(self):
        self.valid_key = EncrytionUtil.generate_encryption_key("StrongPass1")
        # Create a temporary file and encrypt it
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b"This is a test file.")
        self.temp_file.close()
        EncrytionUtil.encrypt_file(self.temp_file.name, self.valid_key)

    def tearDown(self):
        # Cleanup: Remove temporary files
        os.remove(self.temp_file.name)
        if os.path.exists(self.temp_file.name + '.enc'):
            os.remove(self.temp_file.name + '.enc')
        decrypted_file_path = self.temp_file.name.replace('.enc', '')
        if os.path.exists(decrypted_file_path):
            os.remove(decrypted_file_path)

    def test_decrypting_valid_encrypted_file(self):
        EncrytionUtil.decrypt_file(self.temp_file.name + '.enc', self.valid_key)
        decrypted_file_path = self.temp_file.name.replace('.enc', '')
        self.assertTrue(os.path.exists(decrypted_file_path))

    def test_with_non_existent_encrypted_file_path(self):
        with self.assertRaises(FileNotFoundError):
            EncrytionUtil.decrypt_file("non_existent_file.txt.enc", self.valid_key)

    def test_decrypting_with_invalid_key(self):
        with self.assertRaises(ValueError):
            EncrytionUtil.decrypt_file(self.temp_file.name + '.enc', 'invalidkey')


class TestIsEncrypted(unittest.TestCase):

    def setUp(self):
        self.valid_key = EncrytionUtil.generate_encryption_key("StrongPass1")
        # Create a temporary file and encrypt it
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b"This is a test file.")
        self.temp_file.close()
        EncrytionUtil.encrypt_file(self.temp_file.name, self.valid_key)

        # Create a non-encrypted temporary file
        self.non_encrypted_file = tempfile.NamedTemporaryFile(delete=False)
        self.non_encrypted_file.write(b"This is a non-encrypted test file.")
        self.non_encrypted_file.close()

    def tearDown(self):
        # Cleanup: Remove temporary files
        os.remove(self.temp_file.name)
        if os.path.exists(self.temp_file.name + '.enc'):
            os.remove(self.temp_file.name + '.enc')
        os.remove(self.non_encrypted_file.name)

    def test_with_encrypted_file(self):
        self.assertTrue(EncrytionUtil.is_encrypted(self.temp_file.name + '.enc', self.valid_key))

    def test_with_non_encrypted_file(self):
        self.assertFalse(EncrytionUtil.is_encrypted(self.non_encrypted_file.name, self.valid_key))


class TestDecompressFile(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()

        # Create a temporary zip file with some content
        self.temp_zip_file = os.path.join(self.temp_dir, 'test.zip')
        with zipfile.ZipFile(self.temp_zip_file, 'w') as zipf:
            zipf.writestr('test.txt', 'This is a test file.')

    def tearDown(self):
        # Cleanup: Remove temporary directory and its contents
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_decompressing_valid_zip_file(self):
        EncrytionUtil.decompress_file(self.temp_zip_file, self.temp_dir)
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'test.txt')))

    def test_with_non_existent_zip_file_path(self):
        with self.assertRaises(FileNotFoundError):
            EncrytionUtil.decompress_file("non_existent_file.zip", self.temp_dir)

    def test_with_invalid_zip_file(self):
        invalid_zip_file = os.path.join(self.temp_dir, 'invalid.zip')
        with open(invalid_zip_file, 'w') as f:
            f.write("This is not a zip file.")
        with self.assertRaises(zipfile.BadZipFile):
            EncrytionUtil.decompress_file(invalid_zip_file, self.temp_dir)


class TestCompressFile(unittest.TestCase):

    def setUp(self):
        # Create a temporary file with some test data
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b"This is a test file.")
        self.temp_file.close()

    def tearDown(self):
        # Cleanup: Remove temporary files
        os.remove(self.temp_file.name)
        if os.path.exists(self.temp_file.name + '.zip'):
            os.remove(self.temp_file.name + '.zip')

    def test_compressing_valid_file(self):
        EncrytionUtil.compress_file(self.temp_file.name)
        self.assertTrue(os.path.exists(self.temp_file.name + '.zip'))

    def test_with_non_existent_file_path(self):
        with self.assertRaises(FileNotFoundError):
            EncrytionUtil.compress_file("non_existent_file.txt")


class TestBinaryToHex(unittest.TestCase):

    def test_with_valid_binary_data(self):
        # Test a variety of binary data
        self.assertEqual(EncrytionUtil.binary_to_hex(b'\x00\x0F'), '000f')
        self.assertEqual(EncrytionUtil.binary_to_hex(b'hello'), '68656c6c6f')
        self.assertEqual(EncrytionUtil.binary_to_hex(b'\xff\xfe\xfd\xfc'), 'fffefdfc')

    def test_with_empty_bytes(self):
        self.assertEqual(EncrytionUtil.binary_to_hex(b''), '')


class TestCreateHash(unittest.TestCase):

    def test_hashing_with_default_algorithm(self):
        data = "test"
        expected_hash = hashlib.sha256(data.encode()).hexdigest()
        self.assertEqual(EncrytionUtil.create_hash(data), expected_hash)

    def test_hashing_with_different_algorithms(self):
        data = "test"
        algorithms = ['sha1', 'sha224', 'sha384', 'sha512']
        for algo in algorithms:
            with self.subTest(algorithm=algo):
                expected_hash = hashlib.new(algo, data.encode()).hexdigest()
                self.assertEqual(EncrytionUtil.create_hash(data, algo), expected_hash)

    def test_with_unsupported_algorithm(self):
        with self.assertRaises(ValueError):
            EncrytionUtil.create_hash("test", "unsupported_algo")


class TestDecodeBase64(unittest.TestCase):

    def test_with_valid_base64_encoded_strings(self):
        # Test a variety of valid base64 encoded strings
        test_cases = [
            ("SGVsbG8sIFdvcmxkIQ==", "Hello, World!"),
            ("VGhpcyBpcyBhIHRlc3Q=", "This is a test"),
            ("c29tZSBieXRlcw==", "some bytes")
        ]
        for encoded, original in test_cases:
            with self.subTest(encoded=encoded):
                self.assertEqual(EncrytionUtil.decode_base64(encoded), original)

    def test_with_invalid_base64_string(self):
        invalid_data = "This is not base64!"
        with self.assertRaises(Exception):  # Replace Exception with the specific exception if known
            EncrytionUtil.decode_base64(invalid_data)

    def test_with_empty_string(self):
        self.assertEqual(EncrytionUtil.decode_base64(""), "")

        
class TestEncodeBase64(unittest.TestCase):

    def test_with_valid_strings(self):
        # Test a variety of strings
        test_cases = [
            ("Hello, World!", "SGVsbG8sIFdvcmxkIQ=="),
            ("This is a test", "VGhpcyBpcyBhIHRlc3Q="),
            ("some bytes", "c29tZSBieXRlcw==")
        ]
        for original, encoded in test_cases:
            with self.subTest(original=original):
                self.assertEqual(EncrytionUtil.encode_base64(original), encoded)

    def test_with_empty_string(self):
        self.assertEqual(EncrytionUtil.encode_base64(""), "")


if __name__ == '__main__':
    unittest.main()
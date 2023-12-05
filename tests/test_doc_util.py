import os
import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path
from lionagi.utils.doc_util import (
    dir_to_path,
    read_text,
    dir_to_files,
    chunk_text,
    file_to_chunks,
    get_bins,
)


class Test_doc_util(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        # Clean up the temporary directory after each test
        self.temp_dir.cleanup()

    def test_dir_to_path(self):
        # Mock the 'glob' method to avoid actual file system operations
        with patch('lionagi.utils.doc_util.Path.glob') as mock_glob:
            mock_glob.return_value = [Path(self.temp_dir.name) / 'file1.txt', Path(self.temp_dir.name) / 'file2.txt']
            result = dir_to_path(dir=self.temp_dir.name, ext='.txt', recursive=True, flat=True)
        expected_result = [Path(self.temp_dir.name) / 'file1.txt', Path(self.temp_dir.name) / 'file2.txt']
        self.assertEqual(result, expected_result)

    def test_read_text(self):
        # Create a temporary file with known content
        with open(Path(self.temp_dir.name) / 'temp_test_file.txt', 'w') as temp_file:
            temp_file.write('Hello, World!')

        result = read_text(filepath=str(Path(self.temp_dir.name) / 'temp_test_file.txt'), clean=True)
        self.assertEqual(result, 'Hello, World!')

    def test_dir_to_files(self):
        with open(Path(self.temp_dir.name) / 'file1.txt', 'w') as file1:
            file1.write('Hello, World!')
        with open(Path(self.temp_dir.name) / 'file2.txt', 'w') as file2:
            file2.write('LionAGI is cool!')

        result = dir_to_files(dir=self.temp_dir.name, ext='.txt', to_csv=False)

        expected_result = [
            {'project': 'project', 'folder': os.path.basename(self.temp_dir.name), 'file': 'file2.txt', 'file_size': 16,
             'content': 'LionAGI is cool!'},
            {'project': 'project', 'folder': os.path.basename(self.temp_dir.name), 'file': 'file1.txt', 'file_size': 13,
             'content': 'Hello, World!'},
        ]
        self.assertEqual(result, expected_result)

    def test_chunk_text(self):
        result = chunk_text("This is a test string.", 10, 0.2, 1)
        expected_result =  ['This is a t', ' test string', 'ng.']
        self.assertEqual(result, expected_result)

    def test_file_to_chunks(self):
        # Mock chunk_text to avoid actual text chunking
        fileinput = [
            {'project': 'project', 'folder': os.path.basename(self.temp_dir.name), 'file': 'file2.txt', 'file_size': 16,
             'content': 'LionAGI is cool!'},
            {'project': 'project', 'folder': os.path.basename(self.temp_dir.name), 'file': 'file1.txt', 'file_size': 13,
             'content': 'Hello, World!'},
        ]
        result = file_to_chunks(fileinput, chunk_size=10, threshold=5)
        expected_result = [{'chunk_content': 'LionAGI is ', 'chunk_id': 1, 'chunk_overlap': 0.2, 'chunk_size': 11,
                            'chunk_threshold': 5, 'file': 'file2.txt', 'file_chunks': 2, 'file_size': 16,
                            'folder': os.path.basename(self.temp_dir.name), 'project': 'project'},
                           {'chunk_content': 's cool!', 'chunk_id': 2, 'chunk_overlap': 0.2, 'chunk_size': 7,
                            'chunk_threshold': 5, 'file': 'file2.txt', 'file_chunks': 2, 'file_size': 16,
                            'folder': os.path.basename(self.temp_dir.name), 'project': 'project'},
                           {'chunk_content': 'Hello, World!', 'chunk_id': 1, 'chunk_overlap': 0.2, 'chunk_size': 13,
                            'chunk_threshold': 5, 'file': 'file1.txt', 'file_chunks': 1, 'file_size': 13,
                            'folder': os.path.basename(self.temp_dir.name), 'project': 'project'}]
        self.assertEqual(result, expected_result)

    def test_get_bins(self):
        result = get_bins(['apple', 'a', 'b', 'banana', 'cheery', 'c', 'd', 'e'], upper=10)
        expected_result = [[0, 1, 2], [3], [4, 5, 6, 7]]
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()

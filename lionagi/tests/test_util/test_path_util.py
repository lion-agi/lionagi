import shutil
import tempfile
import unittest
from pathlib import Path

from lionagi.util.path_util import PathUtil


class TestPathUtil(unittest.TestCase):

    def test_split_path_file(self):
        """Test splitting a file path."""
        parent, name = PathUtil.split_path("/tmp/example.txt")
        self.assertEqual(parent, Path("/tmp"))
        self.assertEqual(name, "example.txt")

    def test_split_path_directory(self):
        """Test splitting a directory path."""
        parent, name = PathUtil.split_path("/tmp/example/")
        self.assertEqual(parent, Path("/tmp"))
        self.assertEqual(name, "example")

    def test_split_path_root(self):
        """Test splitting the root path."""
        parent, name = PathUtil.split_path("/")
        self.assertEqual(parent, Path("/"))
        self.assertEqual(name, "")
        
        
class TestPathUtil2(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        # Create some test files
        Path(self.test_dir, 'test_file.txt').touch()
        Path(self.test_dir, 'another_test_file.md').touch()

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_list_files_no_extension(self):
        files = PathUtil.list_files(self.test_dir)
        self.assertEqual(len(files), 2)  # Expecting 2 files

    def test_list_files_with_extension(self):
        files = PathUtil.list_files(self.test_dir, extension='txt')
        self.assertEqual(len(files), 1)  # Expecting 1 .txt file
        self.assertTrue(files[0].name.endswith('.txt'))
        
if __name__ == '__main__':
    unittest.main()

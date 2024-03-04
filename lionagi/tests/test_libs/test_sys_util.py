import unittest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
import shutil
import tempfile
import time
import sys
from pathlib import Path

from lionagi.libs.sys_util import SysUtil


class TestSysUtil(unittest.TestCase):

    def test_sleep(self):
        start = time.time()
        SysUtil.sleep(0.1)  # Sleep for 0.1 seconds
        end = time.time()
        self.assertTrue((end - start) >= 0.1)

    def test_get_now(self):
        # Test returning Unix timestamp
        timestamp = time.time()
        self.assertIsInstance(timestamp, float)

        # Test returning datetime object
        now = SysUtil.get_now(datetime_=True)
        self.assertIsInstance(now, datetime)

    def test_change_dict_key(self):
        dict_ = {"old_key": "value"}
        SysUtil.change_dict_key(dict_, "old_key", "new_key")
        self.assertIn("new_key", dict_)
        self.assertNotIn("old_key", dict_)

    def test_get_timestamp(self):
        timestamp = SysUtil.get_timestamp()
        self.assertIsInstance(timestamp, str)
        # Test custom separator
        custom_sep_timestamp = SysUtil.get_timestamp(sep="-")
        self.assertIn("-", custom_sep_timestamp)

    def test_create_copy(self):
        input_ = {"key": "value"}
        # Single copy
        single_copy = SysUtil.create_copy(input_)
        self.assertEqual(input_, single_copy)
        self.assertNotEqual(id(input_), id(single_copy))
        # Multiple copies
        copies = SysUtil.create_copy(input_, 2)
        self.assertIsInstance(copies, list)
        self.assertEqual(len(copies), 2)
        self.assertNotEqual(id(copies[0]), id(copies[1]))

    def test_create_id(self):
        id1 = SysUtil.create_id()
        id2 = SysUtil.create_id()
        self.assertIsInstance(id1, str)
        self.assertEqual(len(id1), 32)
        self.assertNotEqual(id1, id2)

    def test_get_bins(self):
        input_ = ["a" * 500, "b" * 1000, "c" * 500, "d" * 1000]
        bins = SysUtil.get_bins(input_)
        self.assertEqual(len(bins), 2)
        self.assertEqual(bins, [[0, 1], [2, 3]])

    def test_get_cpu_architecture(self):
        architecture = SysUtil.get_cpu_architecture()
        self.assertIn(architecture, ["apple_silicon", "other_cpu"])

    def test_is_package_installed(self):
        with patch("importlib.util.find_spec", return_value=None):
            self.assertFalse(SysUtil.is_package_installed("nonexistent_package"))
        with patch("importlib.util.find_spec", return_value=True):
            self.assertTrue(SysUtil.is_package_installed("existent_package"))

    @patch(
        "importlib.metadata.distributions",
        return_value=[type("", (), {"metadata": {"Name": "fake-package"}})()],
    )
    def test_list_installed_packages(self, mock_distributions):
        installed_packages = SysUtil.list_installed_packages()
        self.assertIn("fake-package", installed_packages)

    @patch("subprocess.check_call")
    def test_uninstall_package(self, mock_subprocess):
        SysUtil.uninstall_package("fake-package")
        mock_subprocess.assert_called_with(
            [sys.executable, "-m", "pip", "uninstall", "fake-package", "-y"]
        )

    @patch("subprocess.check_call")
    def test_update_package(self, mock_subprocess):
        SysUtil.update_package("fake-package")
        mock_subprocess.assert_called_with(
            [sys.executable, "-m", "pip", "install", "--upgrade", "fake-package"]
        )

    def test_split_path_file(self):
        """Test splitting a file path."""
        parent, name = SysUtil.split_path("/tmp/example.txt")
        self.assertEqual(parent, Path("/tmp"))
        self.assertEqual(name, "example.txt")

    def test_split_path_directory(self):
        """Test splitting a directory path."""
        parent, name = SysUtil.split_path("/tmp/example/")
        self.assertEqual(parent, Path("/tmp"))
        self.assertEqual(name, "example")

    def test_split_path_root(self):
        """Test splitting the root path."""
        parent, name = SysUtil.split_path("/")
        self.assertEqual(parent, Path("/"))
        self.assertEqual(name, "")

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        # Create some test files
        Path(self.test_dir, "test_file.txt").touch()
        Path(self.test_dir, "another_test_file.md").touch()

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_list_files_no_extension(self):
        files = SysUtil.list_files(self.test_dir)
        self.assertEqual(len(files), 2)  # Expecting 2 files

    def test_list_files_with_extension(self):
        files = SysUtil.list_files(self.test_dir, extension="txt")
        self.assertEqual(len(files), 1)  # Expecting 1 .txt file
        self.assertTrue(files[0].name.endswith(".txt"))

    def test_change_existing_key(self):
        test_dict = {"old_key": "value"}
        SysUtil.change_dict_key(test_dict, "old_key", "new_key")
        self.assertIn("new_key", test_dict)
        self.assertNotIn("old_key", test_dict)

    def test_change_non_existing_key(self):
        test_dict = {"key": "value"}
        SysUtil.change_dict_key(test_dict, "non_existing_key", "new_key")
        self.assertNotIn("new_key", test_dict)
        self.assertIn("key", test_dict)

    def test_change_key_to_existing_key(self):
        test_dict = {"old_key": "value1", "new_key": "value2"}
        SysUtil.change_dict_key(test_dict, "old_key", "new_key")
        self.assertEqual(test_dict["new_key"], "value1")

    def test_default_separator(self):
        timestamp = SysUtil.get_timestamp()
        self.assertNotIn(":", timestamp)
        self.assertNotIn(".", timestamp)

    def test_custom_separator(self):
        timestamp = SysUtil.get_timestamp(sep="-")
        self.assertNotIn(":", timestamp)
        self.assertNotIn(".", timestamp)
        self.assertIn("-", timestamp)

    def test_valid_schema(self):
        test_dict = {"key1": 1, "key2": "value"}
        schema = {"key1": int, "key2": str}
        self.assertTrue(SysUtil.is_schema(test_dict, schema))

    def test_invalid_schema(self):
        test_dict = {"key1": "value", "key2": "value"}
        schema = {"key1": int, "key2": str}
        self.assertFalse(SysUtil.is_schema(test_dict, schema))

    def test_partial_schema(self):
        test_dict = {"key1": 1}
        schema = {"key1": int, "key2": str}
        self.assertFalse(SysUtil.is_schema(test_dict, schema))

    def test_single_copy(self):
        original = {"key": "value"}
        copy = SysUtil.create_copy(original)
        self.assertEqual(original, copy)
        self.assertNotEqual(id(original), id(copy))

    def test_multiple_copies(self):
        original = {"key": "value"}
        copies = SysUtil.create_copy(original, num=2)
        self.assertEqual(len(copies), 2)
        self.assertNotEqual(id(copies[0]), id(copies[1]))

    def test_invalid_num(self):
        with self.assertRaises(ValueError):
            SysUtil.create_copy({}, num=0)

    def test_id_length(self):
        id_ = SysUtil.create_id()
        self.assertEqual(len(id_), 32)

    def test_custom_length(self):
        id_ = SysUtil.create_id(n=16)
        self.assertEqual(len(id_), 16)

    def test_bins_with_small_strings(self):
        input_ = ["a", "b", "c", "d"]
        bins = SysUtil.get_bins(input_, upper=2)
        self.assertEqual(len(bins), 4)

    def test_bins_with_large_strings(self):
        input_ = ["a" * 1000, "b" * 1000, "c" * 1000]
        bins = SysUtil.get_bins(input_)
        self.assertEqual(len(bins), 3)

    def test_bins_with_empty_input(self):
        bins = SysUtil.get_bins([])
        self.assertEqual(len(bins), 0)


if __name__ == "__main__":
    unittest.main()

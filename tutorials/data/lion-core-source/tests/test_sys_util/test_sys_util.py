# import os
# from datetime import datetime, timezone
# from pathlib import Path
# from unittest.mock import MagicMock, patch

# import pytest

# from lionabc import Observable
# from lionabc.exceptions import LionIDError
# from lion_core.setting import LionIDConfig
# from lion_core.sys_utils import SysUtil


# class TestSysUtilTime:
#     def test_time_timestamp(self):
#         result = SysUtil.time(type_="timestamp")
#         assert isinstance(result, float)
#         assert result > 0

#     def test_time_datetime(self):
#         result = SysUtil.time(type_="datetime")
#         assert isinstance(result, datetime)
#         assert result.tzinfo == timezone.utc

#     def test_time_iso(self):
#         result = SysUtil.time(type_="iso")
#         assert isinstance(result, str)
#         assert "T" in result
#         assert result.endswith("Z") or result.endswith("+00:00")

#     def test_time_custom(self):
#         custom_format = "%Y-%m-%d %H:%M:%S"
#         result = SysUtil.time(type_="custom", custom_format=custom_format)
#         assert isinstance(result, str)
#         assert datetime.strptime(result, custom_format)

#     def test_time_invalid_type(self):
#         with pytest.raises(ValueError):
#             SysUtil.time(type_="invalid")

#     def test_time_custom_without_format(self):
#         with pytest.raises(ValueError):
#             SysUtil.time(type_="custom")

#     def test_time_custom_sep(self):
#         result = SysUtil.time(
#             type_="custom", custom_format="%Y-%m-%d %H:%M:%S", custom_sep="_"
#         )
#         assert "_" in result
#         assert "-" not in result

#     def test_time_timestamp(self):
#         result = SysUtil.time(type_="timestamp")
#         assert isinstance(result, float)
#         assert result > 0

#     def test_time_datetime(self):
#         result = SysUtil.time(type_="datetime")
#         assert isinstance(result, datetime)
#         assert result.tzinfo == timezone.utc

#     def test_time_iso(self):
#         result = SysUtil.time(type_="iso")
#         assert isinstance(result, str)
#         assert "T" in result
#         assert result.endswith("Z") or result.endswith("+00:00")

#     def test_time_custom(self):
#         custom_format = "%Y-%m-%d %H:%M:%S"
#         result = SysUtil.time(type_="custom", custom_format=custom_format)
#         assert isinstance(result, str)
#         assert datetime.strptime(result, custom_format)

#     def test_time_invalid_type(self):
#         with pytest.raises(ValueError):
#             SysUtil.time(type_="invalid")

#     def test_time_custom_without_format(self):
#         with pytest.raises(ValueError):
#             SysUtil.time(type_="custom")


# class TestSysUtilCopy:
#     @pytest.fixture
#     def temp_directory(self, tmp_path):
#         base_dir = tmp_path / "test_dir"
#         base_dir.mkdir()
#         (base_dir / "file1.txt").write_text("content1")
#         (base_dir / "file2.py").write_text("content2")
#         sub_dir = base_dir / "subdir"
#         sub_dir.mkdir()
#         (sub_dir / "file3.txt").write_text("content3")
#         return base_dir

#     def test_copy_file(self, temp_directory):
#         src = temp_directory / "file1.txt"
#         dest = temp_directory / "copy_of_file1.txt"
#         SysUtil.copy_file(src, dest)
#         assert dest.exists()
#         assert dest.read_text() == "content1"

#     def test_copy_file_non_existent_source(self, temp_directory):
#         src = temp_directory / "non_existent.txt"
#         dest = temp_directory / "copy.txt"
#         with pytest.raises(FileNotFoundError):
#             SysUtil.copy_file(src, dest)

#     def test_copy_file_permission_error(self, temp_directory):
#         src = temp_directory / "file1.txt"
#         dest = temp_directory / "no_permission.txt"
#         with patch("lion_core.sys_utils.copy2", side_effect=PermissionError):
#             with pytest.raises(PermissionError):
#                 SysUtil.copy_file(src, dest)

#     def test_copy_file_os_error(self, temp_directory):
#         src = temp_directory / "file1.txt"
#         dest = temp_directory / "os_error.txt"
#         with patch("lion_core.sys_utils.copy2", side_effect=OSError):
#             with pytest.raises(OSError):
#                 SysUtil.copy_file(src, dest)

#     def test_copy_file_overwrite(self, temp_directory):
#         src = temp_directory / "file1.txt"
#         dest = temp_directory / "file2.py"
#         SysUtil.copy_file(src, dest)
#         assert dest.read_text() == "content1"

#     def test_copy_file_to_new_directory(self, temp_directory):
#         src = temp_directory / "file1.txt"
#         dest = temp_directory / "new_dir" / "copy_of_file1.txt"
#         SysUtil.copy_file(src, dest)
#         assert dest.exists()
#         assert dest.read_text() == "content1"

#     @pytest.mark.skipif(
#         os.name == "nt", reason="Symlinks might not be available on Windows"
#     )
#     def test_copy_file_symlink(self, temp_directory):
#         src = temp_directory / "file1.txt"
#         link = temp_directory / "link_to_file1.txt"
#         link.symlink_to(src)
#         dest = temp_directory / "copy_of_link.txt"
#         SysUtil.copy_file(link, dest)
#         assert dest.exists()
#         assert not dest.is_symlink()
#         assert dest.read_text() == "content1"


# import os
# import re
# from datetime import datetime
# from pathlib import Path
# from unittest.mock import MagicMock, patch

# import pytest

# from lion_core.sys_utils import SysUtil


# class TestSysUtilPathOperations:
#     @pytest.fixture
#     def temp_dir(self, tmp_path):
#         return tmp_path

#     def test_list_files_all(self, temp_dir):
#         (temp_dir / "file1.txt").touch()
#         (temp_dir / "file2.py").touch()
#         subdir = temp_dir / "subdir"
#         subdir.mkdir()
#         (subdir / "file3.txt").touch()

#         files = SysUtil.list_files(temp_dir)
#         assert len(files) == 3
#         assert {f.name for f in files} == {
#             "file1.txt",
#             "file2.py",
#             "file3.txt",
#         }

#     def test_list_files_with_extension(self, temp_dir):
#         (temp_dir / "file1.txt").touch()
#         (temp_dir / "file2.py").touch()
#         (temp_dir / "subdir").mkdir()
#         (temp_dir / "subdir" / "file3.txt").touch()

#         files = SysUtil.list_files(temp_dir, "txt")
#         assert len(files) == 2
#         assert {f.name for f in files} == {"file1.txt", "file3.txt"}

#     def test_list_files_empty_directory(self, temp_dir):
#         files = SysUtil.list_files(temp_dir)
#         assert len(files) == 0

#     def test_list_files_non_existent_directory(self):
#         with pytest.raises(NotADirectoryError):
#             SysUtil.list_files("/non/existent/directory")

#     def test_list_files_file_as_input(self, temp_dir):
#         file_path = temp_dir / "test.txt"
#         file_path.touch()
#         with pytest.raises(NotADirectoryError):
#             SysUtil.list_files(file_path)

#     def test_split_path(self):
#         path = Path("/home/user/documents/file.txt")
#         dir_path, filename = SysUtil.split_path(path)
#         assert dir_path == Path("/home/user/documents")
#         assert filename == "file.txt"

#     def test_split_path_just_filename(self):
#         path = "file.txt"
#         dir_path, filename = SysUtil.split_path(path)
#         assert dir_path == Path(".")
#         assert filename == "file.txt"

#     def test_split_path_root(self):
#         path = "/"
#         dir_path, filename = SysUtil.split_path(path)
#         assert dir_path == Path("/")
#         assert filename == ""

#     def test_get_file_size_file(self, temp_dir):
#         file_path = temp_dir / "test.txt"
#         file_path.write_text("content")
#         size = SysUtil.get_file_size(file_path)
#         assert size == 7  # "content" is 7 bytes

#     def test_get_file_size_directory(self, temp_dir):
#         (temp_dir / "file1.txt").write_text("content1")
#         (temp_dir / "file2.txt").write_text("content2")
#         size = SysUtil.get_file_size(temp_dir)
#         assert size == 16  # "content1" + "content2" = 8 + 8 = 16 bytes

#     def test_get_file_size_non_existent(self):
#         with pytest.raises(FileNotFoundError):
#             SysUtil.get_file_size("/non/existent/path")

#     def test_get_file_size_permission_error(self, temp_dir):
#         with patch.object(Path, "stat", side_effect=PermissionError):
#             with pytest.raises(PermissionError):
#                 SysUtil.get_file_size(temp_dir)

#     def test_get_file_size_empty_dir(self, temp_dir):
#         assert SysUtil.get_file_size(temp_dir) == 0


# class TestSysUtilPathCreation:
#     @pytest.fixture
#     def temp_dir(self, tmp_path):
#         return tmp_path

#     def test_create_path_basic(self, temp_dir):
#         path = SysUtil.create_path(temp_dir, "test.txt")
#         assert path.parent == temp_dir
#         assert path.name == "test.txt"
#         assert (
#             not path.exists()
#         )  # File should not be created, only path returned

#     def test_create_path_with_timestamp(self, temp_dir):
#         path = SysUtil.create_path(temp_dir, "test.txt", timestamp=True)
#         assert path.parent == temp_dir
#         assert re.match(r"test_\d{14}\.txt", path.name)

#     def test_create_path_with_timestamp_prefix(self, temp_dir):
#         path = SysUtil.create_path(
#             temp_dir, "test.txt", timestamp=True, time_prefix=True
#         )
#         assert path.parent == temp_dir
#         assert re.match(r"\d{14}_test\.txt", path.name)

#     def test_create_path_custom_timestamp(self, temp_dir):
#         path = SysUtil.create_path(
#             temp_dir, "test.txt", timestamp=True, timestamp_format="%Y%m%d"
#         )
#         assert path.parent == temp_dir
#         assert re.match(r"test_\d{8}\.txt", path.name)

#     def test_create_path_with_random_hash(self, temp_dir):
#         path = SysUtil.create_path(temp_dir, "test.txt", random_hash_digits=5)
#         assert path.parent == temp_dir
#         assert re.match(r"test-[a-f0-9]{5}\.txt", path.name)

#     def test_create_path_file_exists(self, temp_dir):
#         existing_file = temp_dir / "existing.txt"
#         existing_file.touch()
#         path = SysUtil.create_path(
#             temp_dir, "existing.txt", file_exist_ok=True
#         )
#         assert path == existing_file
#         assert path.exists()

#     def test_create_path_file_exists_not_ok(self, temp_dir):
#         existing_file = temp_dir / "existing.txt"
#         existing_file.touch()
#         with pytest.raises(FileExistsError):
#             SysUtil.create_path(temp_dir, "existing.txt", file_exist_ok=False)

#     def test_create_path_nested_directory(self, temp_dir):
#         nested_dir = temp_dir / "nested" / "dir"
#         path = SysUtil.create_path(nested_dir, "test.txt")
#         assert path.parent == nested_dir
#         assert path.name == "test.txt"
#         assert nested_dir.exists()  # Directory should be created
#         assert not path.exists()  # File should not be created

#     def test_create_path_invalid_filename(self, temp_dir):
#         with pytest.raises(ValueError):
#             SysUtil.create_path(temp_dir, "invalid/filename.txt")

#     def test_create_path_all_options(self, temp_dir):
#         path = SysUtil.create_path(
#             temp_dir,
#             "test.txt",
#             timestamp=True,
#             time_prefix=True,
#             random_hash_digits=5,
#             timestamp_format="%Y%m%d",
#         )
#         assert path.parent == temp_dir
#         assert re.match(r"\d{8}_test-[a-f0-9]{5}\.txt", path.name)


# class TestSysUtilFileOperations:
#     @pytest.fixture
#     def temp_dir(self, tmp_path):
#         return tmp_path

#     def test_save_to_file(self, temp_dir):
#         text = "Hello, World!"
#         file_path = SysUtil.save_to_file(
#             text, temp_dir, "test.txt", timestamp=False, random_hash_digits=0
#         )
#         assert file_path.exists()
#         assert file_path.read_text() == text

#     def test_save_to_file_with_timestamp(self, temp_dir):
#         text = "Hello, World!"
#         file_path = SysUtil.save_to_file(
#             text, temp_dir, "test.txt", timestamp=True
#         )
#         assert file_path.exists()
#         assert file_path.read_text() == text
#         assert re.match(r"test_\d{14}\.txt", file_path.name)

#     def test_save_to_file_with_random_hash(self, temp_dir):
#         text = "Hello, World!"
#         file_path = SysUtil.save_to_file(
#             text, temp_dir, "test.txt", timestamp=False, random_hash_digits=6
#         )
#         assert file_path.exists()
#         assert file_path.read_text() == text
#         assert re.match(r"test-[a-f0-9]{6}\.txt", file_path.name)

#     def test_read_file(self, temp_dir):
#         text = "Hello, World!"
#         file_path = temp_dir / "test.txt"
#         file_path.write_text(text)
#         result = SysUtil.read_file(file_path)
#         assert result == text

#     def test_read_file_not_found(self, temp_dir):
#         non_existent_file = temp_dir / "non_existent.txt"
#         with pytest.raises(FileNotFoundError):
#             SysUtil.read_file(non_existent_file)

#     def test_save_to_file_nested_directory(self, temp_dir):
#         text = "Hello, World!"
#         nested_dir = temp_dir / "nested" / "dir"
#         file_path = SysUtil.save_to_file(text, nested_dir, "test.txt")
#         assert file_path.exists()
#         assert file_path.read_text() == text

#     def test_save_to_file_overwrite(self, temp_dir):
#         file_path = temp_dir / "test.txt"

#         SysUtil.save_to_file(
#             "Original", temp_dir, "test.txt", file_exist_ok=True
#         )
#         SysUtil.save_to_file(
#             "Updated", temp_dir, "test.txt", file_exist_ok=True
#         )
#         assert file_path.read_text() == "Updated"

#     @pytest.mark.parametrize(
#         "filename",
#         [
#             "normal.txt",
#             "with spaces.txt",
#             "with-dashes.txt",
#             "with_underscores.txt",
#             "with.multiple.dots.txt",
#             "တောင်ကြီးမြို့.txt",  # Non-ASCII characters
#             "🐍.py",  # Emoji
#         ],
#     )
#     def test_file_operations_with_special_filenames(self, temp_dir, filename):
#         content = "Test content"
#         file_path = SysUtil.save_to_file(content, temp_dir, filename)
#         assert file_path.exists()
#         assert SysUtil.read_file(file_path) == content

#     @pytest.mark.skipif(
#         os.name == "nt", reason="Symlinks might not be available on Windows"
#     )
#     def test_file_operations_with_symlink(self, temp_dir):
#         original = temp_dir / "original.txt"
#         SysUtil.save_to_file("Original content", temp_dir, "original.txt")
#         symlink = temp_dir / "symlink.txt"
#         symlink.symlink_to(original)

#         # Test reading through symlink
#         content = SysUtil.read_file(symlink)
#         assert content == "Original content"

#         # Test file size through symlink
#         size = SysUtil.get_file_size(symlink)
#         assert size == len("Original content")


# import importlib
# import subprocess
# from unittest.mock import MagicMock, patch

# import pytest

# from lion_core.sys_utils import SysUtil


# class TestSysUtilImportMethods:

#     @patch("lion_core.sys_utils.SysUtil.import_module")
#     @patch("lion_core.sys_utils._run_pip_command")
#     def test_install_import_success(self, mock_run_pip, mock_import):
#         mock_import.side_effect = [ImportError, MagicMock()]

#         result = SysUtil.install_import("test_package")

#         assert mock_run_pip.called
#         assert mock_import.call_count == 2
#         assert result is not None

#     @patch("lion_core.sys_utils.SysUtil.import_module")
#     @patch("lion_core.sys_utils._run_pip_command")
#     def test_install_import_failure(self, mock_run_pip, mock_import):
#         mock_import.side_effect = ImportError
#         mock_run_pip.side_effect = subprocess.CalledProcessError(1, "pip")

#         with pytest.raises(ImportError):
#             SysUtil.install_import("test_package")

#     @patch("builtins.__import__")
#     def test_import_module_success(self, mock_import):
#         mock_module = MagicMock()
#         mock_module.TestClass = "TestClass"
#         mock_import.return_value = mock_module

#         result = SysUtil.import_module(
#             "test_package", "test_module", "TestClass"
#         )

#         assert result == "TestClass"
#         mock_import.assert_called_with(
#             "test_package.test_module", fromlist=["TestClass"]
#         )

#     @patch("builtins.__import__")
#     def test_import_module_without_module_name(self, mock_import):
#         mock_module = MagicMock()
#         mock_import.return_value = mock_module

#         result = SysUtil.import_module("test_package")

#         assert result == mock_module
#         mock_import.assert_called_with("test_package")

#     @patch("builtins.__import__")
#     def test_import_module_with_multiple_import_names(self, mock_import):
#         mock_module = MagicMock()
#         mock_module.Class1 = "Class1"
#         mock_module.Class2 = "Class2"
#         mock_import.return_value = mock_module

#         result = SysUtil.import_module(
#             "test_package", "test_module", ["Class1", "Class2"]
#         )

#         assert result == ["Class1", "Class2"]
#         mock_import.assert_called_with(
#             "test_package.test_module", fromlist=["Class1", "Class2"]
#         )

#     def test_import_module_failure(self):
#         with pytest.raises(ImportError):
#             SysUtil.import_module("non_existent_package")

#     @patch("importlib.util.find_spec")
#     def test_is_package_installed_true(self, mock_find_spec):
#         mock_find_spec.return_value = MagicMock()

#         assert SysUtil.is_package_installed("existing_package") is True

#     @patch("importlib.util.find_spec")
#     def test_is_package_installed_false(self, mock_find_spec):
#         mock_find_spec.return_value = None

#         assert SysUtil.is_package_installed("non_existent_package") is False

#     @patch("lion_core.sys_utils.SysUtil.is_package_installed")
#     @patch("lion_core.sys_utils.SysUtil.install_import")
#     @patch("lion_core.sys_utils.SysUtil.import_module")
#     def test_check_import_installed(
#         self, mock_import, mock_install, mock_is_installed
#     ):
#         mock_is_installed.return_value = True
#         mock_import.return_value = MagicMock()

#         result = SysUtil.check_import("existing_package")

#         assert result is not None
#         assert not mock_install.called

#     @patch("lion_core.sys_utils.SysUtil.is_package_installed")
#     @patch("lion_core.sys_utils.SysUtil.install_import")
#     def test_check_import_not_installed_attempt_install(
#         self, mock_install, mock_is_installed
#     ):
#         mock_is_installed.return_value = False
#         mock_install.return_value = MagicMock()

#         result = SysUtil.check_import("new_package", attempt_install=True)

#         assert result is not None
#         assert mock_install.called

#     @patch("lion_core.sys_utils.SysUtil.is_package_installed")
#     def test_check_import_not_installed_no_attempt(self, mock_is_installed):
#         mock_is_installed.return_value = False

#         with pytest.raises(ImportError):
#             SysUtil.check_import("new_package", attempt_install=False)

#     @patch("lion_core.sys_utils.SysUtil.is_package_installed")
#     @patch("lion_core.sys_utils.SysUtil.install_import")
#     def test_check_import_with_custom_error_message(
#         self, mock_install, mock_is_installed
#     ):
#         mock_is_installed.return_value = False

#         with pytest.raises(ImportError, match="Custom error message"):
#             SysUtil.check_import(
#                 "new_package",
#                 attempt_install=False,
#                 error_message="Custom error message",
#             )

#     @patch("importlib.metadata.distributions")
#     def test_list_installed_packages(self, mock_distributions):
#         mock_dist1 = MagicMock()
#         mock_dist1.metadata = {"Name": "package1"}
#         mock_dist2 = MagicMock()
#         mock_dist2.metadata = {"Name": "package2"}
#         mock_distributions.return_value = [mock_dist1, mock_dist2]

#         result = SysUtil.list_installed_packages()

#         assert result == ["package1", "package2"]

#     @patch("importlib.metadata.distributions")
#     def test_list_installed_packages_error(self, mock_distributions):
#         mock_distributions.side_effect = Exception("Test error")

#         result = SysUtil.list_installed_packages()

#         assert result == []

#     @patch("lion_core.sys_utils._run_pip_command")
#     def test_uninstall_package_success(self, mock_run_pip):
#         SysUtil.uninstall_package("test_package")
#         mock_run_pip.assert_called_with(["uninstall", "test_package", "-y"])

#     @patch("lion_core.sys_utils._run_pip_command")
#     def test_uninstall_package_failure(self, mock_run_pip):
#         mock_run_pip.side_effect = subprocess.CalledProcessError(1, "pip")

#         with pytest.raises(subprocess.CalledProcessError):
#             SysUtil.uninstall_package("test_package")

#     @patch("lion_core.sys_utils._run_pip_command")
#     def test_update_package_success(self, mock_run_pip):
#         SysUtil.update_package("test_package")
#         mock_run_pip.assert_called_with(
#             ["install", "--upgrade", "test_package"]
#         )

#     @patch("lion_core.sys_utils._run_pip_command")
#     def test_update_package_failure(self, mock_run_pip):
#         mock_run_pip.side_effect = subprocess.CalledProcessError(1, "pip")

#         with pytest.raises(subprocess.CalledProcessError):
#             SysUtil.update_package("test_package")


# import os
# from pathlib import Path
# from unittest.mock import MagicMock, patch

# import pytest

# from lion_core.sys_utils import SysUtil


# class TestSysUtilAdditional:
#     @pytest.mark.parametrize(
#         "machine,expected",
#         [
#             ("arm64", "arm64"),
#             ("aarch64", "arm64"),
#             ("x86_64", "x86_64"),
#             ("amd64", "x86_64"),
#             ("i386", "i386"),
#             ("powerpc", "powerpc"),
#         ],
#     )
#     def test_get_cpu_architecture(self, machine, expected):
#         with patch("platform.machine", return_value=machine):
#             assert SysUtil.get_cpu_architecture() == expected

#     def test_get_cpu_architecture_unknown(self):
#         with patch("platform.machine", return_value="unknown_arch"):
#             assert SysUtil.get_cpu_architecture() == "unknown_arch"

#     @pytest.mark.skipif(
#         os.name == "nt", reason="Test specific to non-Windows systems"
#     )
#     def test_get_cpu_architecture_apple_silicon(self):
#         with patch("platform.machine", return_value="arm64"):
#             assert SysUtil.get_cpu_architecture() == "arm64"

#     def test_create_path_file_collision(self, tmp_path):
#         # Create the initial file
#         initial_path = SysUtil.create_path(tmp_path, "test.txt")
#         initial_path.touch()

#         # Attempt to create the same file again should raise FileExistsError
#         with pytest.raises(FileExistsError):
#             SysUtil.create_path(tmp_path, "test.txt", file_exist_ok=False)

#         # Creating with file_exist_ok=True should return the existing path
#         existing_path = SysUtil.create_path(
#             tmp_path, "test.txt", file_exist_ok=True
#         )
#         assert existing_path == initial_path

#         # Creating a file with a different name should succeed
#         new_path = SysUtil.create_path(
#             tmp_path, "new_test.txt", file_exist_ok=False
#         )
#         assert new_path != initial_path
#         assert new_path.name == "new_test.txt"

#     def test_get_path_kwargs_simple(self):
#         kwargs = SysUtil._get_path_kwargs("/path/to/file.txt", "txt")
#         assert kwargs["directory"] == Path("/path/to")
#         assert kwargs["filename"] == "file.txt"

#     def test_get_path_kwargs_no_extension(self):
#         kwargs = SysUtil._get_path_kwargs("/path/to/file", "txt")
#         assert kwargs["directory"] == Path("/path/to/file")
#         assert kwargs["filename"] == "new_file.txt"

#     def test_get_path_kwargs_directory_only(self):
#         kwargs = SysUtil._get_path_kwargs("/path/to/dir", "txt")
#         assert kwargs["directory"] == Path("/path/to/dir")
#         assert kwargs["filename"] == "new_file.txt"

#     @pytest.mark.parametrize(
#         "persist_path,postfix,expected",
#         [
#             (
#                 "/path/to/file.csv",
#                 "csv",
#                 {"directory": Path("/path/to"), "filename": "file.csv"},
#             ),
#             (
#                 "/path/to/dir",
#                 "txt",
#                 {
#                     "directory": Path("/path/to/dir"),
#                     "filename": "new_file.txt",
#                 },
#             ),
#             (
#                 "file.json",
#                 "json",
#                 {"directory": Path("."), "filename": "file.json"},
#             ),
#         ],
#     )
#     def test_get_path_kwargs_various_inputs(
#         self, persist_path, postfix, expected
#     ):
#         kwargs = SysUtil._get_path_kwargs(persist_path, postfix)
#         assert kwargs["directory"] == expected["directory"]
#         assert kwargs["filename"] == expected["filename"]

#     def test_large_directory(self, tmp_path):
#         large_dir = tmp_path / "large_dir"
#         large_dir.mkdir()
#         for i in range(10000):
#             (large_dir / f"file_{i}.txt").write_text("content")

#         files = SysUtil.list_files(large_dir)
#         assert len(files) == 10000

#         size = SysUtil.get_file_size(large_dir)
#         assert size == 7 * 10000  # "content" is 7 bytes, 10000 files


# # File: tests/test_sys_utils.py


# import os
# import re
# from datetime import datetime, timezone
# from pathlib import Path
# from shutil import rmtree
# from unittest.mock import patch

# import pytest

# from lionabc import Observable
# from lionabc.exceptions import LionIDError
# from lion_core.setting import LionIDConfig
# from lion_core.sys_utils import SysUtil


# class TestSysUtil:

#     def test_id_default(self):
#         id_ = SysUtil.id()
#         assert isinstance(id_, str)
#         assert len(id_) == 48  # 42 chars + prefix "ln" + 4 hyphens

#     def test_id_custom_length(self):
#         id_ = SysUtil.id(n=20)
#         assert len(id_) == 26  # 20 chars + prefix "ln" + 4 hyphens

#     def test_id_no_hyphens(self):
#         id_ = SysUtil.id(random_hyphen=False)
#         assert "-" not in id_

#     def test_id_custom_prefix_postfix(self):
#         id_ = SysUtil.id(prefix="test_", postfix="_end")
#         assert id_.startswith("test_")
#         assert id_.endswith("_end")

#     def test_get_id_valid(self):
#         class MockObservable(Observable):
#             def __init__(self, ln_id):
#                 self.ln_id = ln_id

#         valid_id = SysUtil.id()
#         mock_obj = MockObservable(valid_id)
#         assert SysUtil.get_id(mock_obj) == valid_id
#         assert SysUtil.get_id(valid_id) == valid_id

#     def test_get_id_invalid(self):
#         with pytest.raises(LionIDError):
#             SysUtil.get_id("invalid_id")

#     def test_get_id_sequence(self):
#         valid_id = SysUtil.id()
#         assert SysUtil.get_id([valid_id]) == valid_id

#     def test_get_id_custom_config(self):
#         custom_config = LionIDConfig(
#             prefix="custom-",
#             n=20,
#             num_hyphens=2,
#             random_hyphen=True,
#             hyphen_start_index=6,
#             hyphen_end_index=-6,
#         )
#         valid_id = "custom-a32eac2f22a-62-a45092f"
#         assert SysUtil.get_id(valid_id, custom_config) == valid_id

#     def test_is_id_valid(self):
#         valid_id = "ln8d7274-45a36cc0-8b89af8b-c5-154c41996cf228d8a5"
#         assert SysUtil.is_id(valid_id) == True

#     def test_is_id_invalid(self):
#         invalid_id = "invalid_id"
#         assert SysUtil.is_id(invalid_id) == False

#     def test_is_id_custom_config(self):
#         custom_config = LionIDConfig(
#             prefix="custom-",
#             n=20,
#             num_hyphens=2,
#             random_hyphen=True,
#             hyphen_start_index=6,
#             hyphen_end_index=-6,
#         )
#         valid_id = "custom-a32eac2f22a-62-a45092f"
#         assert SysUtil.is_id(valid_id, custom_config) == True

#     # Additional tests for edge cases
#     def test_get_id_32_char(self):
#         valid_id = "a" * 32
#         assert SysUtil.get_id(valid_id) == valid_id

#     def test_get_id_invalid_type(self):
#         with pytest.raises(LionIDError):
#             SysUtil.get_id(123)

#     def test_is_id_edge_cases(self):
#         assert SysUtil.is_id("a" * 32) == True
#         assert SysUtil.is_id(123) == False


# import os
# import tempfile
# from datetime import datetime
# from pathlib import Path

# import pytest

# from lion_core.sys_utils import SysUtil


# class TestSysUtilPathMethods:

#     @pytest.fixture
#     def temp_dir(self):
#         with tempfile.TemporaryDirectory() as tmpdirname:
#             yield Path(tmpdirname)

#     def test_clear_path_recursive(self, temp_dir):
#         subdir = temp_dir / "subdir"
#         subdir.mkdir()
#         (subdir / "file.txt").touch()
#         SysUtil.clear_path(temp_dir, recursive=True)
#         assert len(list(temp_dir.iterdir())) == 0

#     def test_create_path_basic(self, temp_dir):
#         path = SysUtil.create_path(temp_dir, "test.txt")
#         assert path.parent == temp_dir
#         assert path.name == "test.txt"

#     def test_create_path_with_timestamp(self, temp_dir):
#         path = SysUtil.create_path(temp_dir, "test.txt", timestamp=True)
#         assert path.parent == temp_dir
#         assert re.match(r"test_\d{14}\.txt", path.name)

#     def test_create_path_custom_timestamp(self, temp_dir):
#         path = SysUtil.create_path(
#             temp_dir, "test.txt", timestamp=True, timestamp_format="%Y%m%d"
#         )
#         assert path.parent == temp_dir
#         assert re.match(r"test_\d{8}\.txt", path.name)

#     def test_create_path_file_exists(self, temp_dir):
#         existing_file = temp_dir / "existing.txt"
#         existing_file.touch()
#         path = SysUtil.create_path(
#             temp_dir, "existing.txt", file_exist_ok=True
#         )
#         assert path == existing_file

#     def test_get_path_kwargs_simple(self):
#         kwargs = SysUtil._get_path_kwargs("/path/to/file.txt", "txt")
#         assert kwargs["directory"] == Path("/path/to")
#         assert kwargs["filename"] == "file.txt"

#     def test_get_path_kwargs_no_extension(self):
#         kwargs = SysUtil._get_path_kwargs("/path/to/file", "txt")
#         assert kwargs["directory"] == Path("/path/to/file")
#         assert kwargs["filename"] == "new_file.txt"

#     def test_get_path_kwargs_directory_only(self):
#         kwargs = SysUtil._get_path_kwargs("/path/to/dir", "txt")
#         assert kwargs["directory"] == Path("/path/to/dir")
#         assert kwargs["filename"] == "new_file.txt"

#     @pytest.mark.parametrize(
#         "persist_path,postfix,expected",
#         [
#             (
#                 "/path/to/file.csv",
#                 "csv",
#                 {"directory": Path("/path/to"), "filename": "file.csv"},
#             ),
#             (
#                 "/path/to/dir",
#                 "txt",
#                 {
#                     "directory": Path("/path/to/dir"),
#                     "filename": "new_file.txt",
#                 },
#             ),
#             (
#                 "file.json",
#                 "json",
#                 {"directory": Path("."), "filename": "file.json"},
#             ),
#         ],
#     )
#     def test_get_path_kwargs_various_inputs(
#         self, persist_path, postfix, expected
#     ):
#         kwargs = SysUtil._get_path_kwargs(persist_path, postfix)
#         assert kwargs["directory"] == expected["directory"]
#         assert kwargs["filename"] == expected["filename"]


# import re
# from datetime import datetime
# from pathlib import Path

# import pytest

# from lion_core.sys_utils import SysUtil


# class TestSysUtilCreatePath:
#     @pytest.fixture
#     def temp_dir(self, tmp_path):
#         return tmp_path

#     def test_create_path_basic(self, temp_dir):
#         path = SysUtil.create_path(temp_dir, "test.txt")
#         assert path.parent == temp_dir
#         assert path.name == "test.txt"
#         assert (
#             not path.exists()
#         )  # File should not be created, only path returned

#     def test_create_path_with_timestamp(self, temp_dir):
#         path = SysUtil.create_path(temp_dir, "test.txt", timestamp=True)
#         assert path.parent == temp_dir
#         assert re.match(r"test_\d{14}\.txt", path.name)

#     def test_create_path_with_timestamp_prefix(self, temp_dir):
#         path = SysUtil.create_path(
#             temp_dir, "test.txt", timestamp=True, time_prefix=True
#         )
#         assert path.parent == temp_dir
#         assert re.match(r"\d{14}_test\.txt", path.name)

#     def test_create_path_custom_timestamp(self, temp_dir):
#         path = SysUtil.create_path(
#             temp_dir, "test.txt", timestamp=True, timestamp_format="%Y%m%d"
#         )
#         assert path.parent == temp_dir
#         assert re.match(r"test_\d{8}\.txt", path.name)

#     def test_create_path_with_random_hash(self, temp_dir):
#         path = SysUtil.create_path(temp_dir, "test.txt", random_hash_digits=5)
#         assert path.parent == temp_dir
#         assert re.match(r"test-[a-f0-9]{5}\.txt", path.name)

#     def test_create_path_file_exists(self, temp_dir):
#         existing_file = temp_dir / "existing.txt"
#         existing_file.touch()
#         path = SysUtil.create_path(
#             temp_dir, "existing.txt", file_exist_ok=True
#         )
#         assert path == existing_file
#         assert path.exists()

#     def test_create_path_file_exists_not_ok(self, temp_dir):
#         existing_file = temp_dir / "existing.txt"
#         existing_file.touch()
#         with pytest.raises(FileExistsError):
#             path = SysUtil.create_path(
#                 temp_dir, "existing.txt", file_exist_ok=False
#             )

#     def test_create_path_nested_directory(self, temp_dir):
#         nested_dir = temp_dir / "nested" / "dir"
#         path = SysUtil.create_path(nested_dir, "test.txt")
#         assert path.parent == nested_dir
#         assert path.name == "test.txt"
#         assert nested_dir.exists()  # Directory should be created
#         assert not path.exists()  # File should not be created

#     def test_create_path_invalid_filename(self, temp_dir):
#         with pytest.raises(ValueError):
#             SysUtil.create_path(temp_dir, "invalid/filename.txt")

#     def test_create_path_all_options(self, temp_dir):
#         path = SysUtil.create_path(
#             temp_dir,
#             "test.txt",
#             timestamp=True,
#             time_prefix=True,
#             random_hash_digits=5,
#             timestamp_format="%Y%m%d",
#         )
#         assert path.parent == temp_dir
#         assert re.match(r"\d{8}_test-[a-f0-9]{5}\.txt", path.name)

#     def test_create_path_file_collision(self, temp_dir):
#         # Create the initial file
#         initial_path = SysUtil.create_path(temp_dir, "test.txt")
#         initial_path.touch()

#         # Attempt to create the same file again should raise FileExistsError
#         with pytest.raises(FileExistsError):
#             SysUtil.create_path(temp_dir, "test.txt", file_exist_ok=False)

#         # Creating with file_exist_ok=True should return the existing path
#         existing_path = SysUtil.create_path(
#             temp_dir, "test.txt", file_exist_ok=True
#         )
#         assert existing_path == initial_path

#         # Creating a file with a different name should succeed
#         new_path = SysUtil.create_path(
#             temp_dir, "new_test.txt", file_exist_ok=False
#         )
#         assert new_path != initial_path
#         assert new_path.name == "new_test.txt"


# @pytest.fixture
# def temp_directory(tmp_path):
#     """Create a temporary directory with some files and subdirectories."""
#     base_dir = tmp_path / "test_dir"
#     base_dir.mkdir()
#     (base_dir / "file1.txt").write_text("content1")
#     (base_dir / "file2.py").write_text("content2")
#     sub_dir = base_dir / "subdir"
#     sub_dir.mkdir()
#     (sub_dir / "file3.txt").write_text("content3")
#     yield base_dir
#     rmtree(base_dir)


# class TestFileUtils:

#     def test_list_files_all(self, temp_directory):
#         files = SysUtil.list_files(temp_directory)
#         assert len(files) == 3
#         assert {f.name for f in files} == {
#             "file1.txt",
#             "file2.py",
#             "file3.txt",
#         }

#     def test_list_files_with_extension(self, temp_directory):
#         files = SysUtil.list_files(temp_directory, "txt")
#         assert len(files) == 2
#         assert {f.name for f in files} == {"file1.txt", "file3.txt"}

#     def test_list_files_empty_directory(self, tmp_path):
#         empty_dir = tmp_path / "empty"
#         empty_dir.mkdir()
#         files = SysUtil.list_files(empty_dir)
#         assert len(files) == 0

#     def test_list_files_non_existent_directory(self):
#         with pytest.raises(NotADirectoryError):
#             SysUtil.list_files("/non/existent/directory")

#     def test_list_files_file_as_input(self, temp_directory):
#         with pytest.raises(NotADirectoryError):
#             SysUtil.list_files(temp_directory / "file1.txt")

#     def test_split_path(self):
#         path = Path("/home/user/documents/file.txt")
#         dir_path, filename = SysUtil.split_path(path)
#         assert dir_path == Path("/home/user/documents")
#         assert filename == "file.txt"

#     def test_split_path_just_filename(self):
#         path = "file.txt"
#         dir_path, filename = SysUtil.split_path(path)
#         assert dir_path == Path(".")
#         assert filename == "file.txt"

#     def test_copy_file(self, temp_directory):
#         src = temp_directory / "file1.txt"
#         dest = temp_directory / "copy_of_file1.txt"
#         SysUtil.copy_file(src, dest)
#         assert dest.exists()
#         assert dest.read_text() == "content1"

#     def test_copy_file_non_existent_source(self, temp_directory):
#         src = temp_directory / "non_existent.txt"
#         dest = temp_directory / "copy.txt"
#         with pytest.raises(FileNotFoundError):
#             SysUtil.copy_file(src, dest)

#     def test_copy_file_permission_error(self, temp_directory):
#         src = temp_directory / "file1.txt"
#         dest = temp_directory / "no_permission.txt"
#         with patch("lion_core.sys_utils.copy2", side_effect=PermissionError):
#             with pytest.raises(PermissionError):
#                 SysUtil.copy_file(src, dest)

#     def test_copy_file_os_error(self, temp_directory):
#         src = temp_directory / "file1.txt"
#         dest = temp_directory / "os_error.txt"
#         with patch("lion_core.sys_utils.copy2", side_effect=OSError):
#             with pytest.raises(OSError):
#                 SysUtil.copy_file(src, dest)

#     def test_get_file_size_file(self, temp_directory):
#         file_path = temp_directory / "file1.txt"
#         size = SysUtil.get_file_size(file_path)
#         assert size == 8  # "content1" is 8 bytes

#     def test_get_file_size_directory(self, temp_directory):
#         size = SysUtil.get_file_size(temp_directory)
#         assert (
#             size == 24
#         )  # Total content size: "content1" + "content2" + "content3" = 8 + 8 + 8 = 24 bytes

#     def test_get_file_size_non_existent(self):
#         with pytest.raises(FileNotFoundError):
#             SysUtil.get_file_size("/non/existent/path")

#     def test_get_file_size_permission_error(self, temp_directory):
#         with patch.object(Path, "stat", side_effect=PermissionError):
#             with pytest.raises(PermissionError):
#                 SysUtil.get_file_size(temp_directory)

#     @pytest.mark.parametrize(
#         "filename",
#         [
#             "normal.txt",
#             "with spaces.txt",
#             "with-dashes.txt",
#             "with_underscores.txt",
#             "with.multiple.dots.txt",
#             "တောင်ကြီးမြို့.txt",  # Non-ASCII characters
#             "🐍.py",  # Emoji
#         ],
#     )
#     def test_file_operations_with_special_filenames(
#         self, temp_directory, filename
#     ):
#         file_path = temp_directory / filename
#         file_path.write_text("content")

#         # Test list_files
#         files = SysUtil.list_files(temp_directory)
#         assert file_path in files

#         # Test split_path
#         dir_path, name = SysUtil.split_path(file_path)
#         assert dir_path == temp_directory
#         assert name == filename

#         # Test copy_file
#         dest_path = temp_directory / f"copy_of_{filename}"
#         SysUtil.copy_file(file_path, dest_path)
#         assert dest_path.exists()

#         # Test get_file_size
#         size = SysUtil.get_file_size(file_path)
#         assert size == 7  # "content" is 7 bytes

#     @pytest.mark.skipif(
#         os.name == "nt", reason="Symlinks might not be available on Windows"
#     )
#     def test_file_operations_with_symlink(self, temp_directory):
#         original = temp_directory / "original.txt"
#         original.write_text("original content")
#         symlink = temp_directory / "symlink.txt"
#         symlink.symlink_to(original)

#         # Test list_files
#         files = SysUtil.list_files(temp_directory)
#         assert symlink in files

#         # Test get_file_size
#         size = SysUtil.get_file_size(symlink)
#         assert size == len("original content")

#     def test_large_directory(self, tmp_path):
#         large_dir = tmp_path / "large_dir"
#         large_dir.mkdir()
#         for i in range(10000):
#             (large_dir / f"file_{i}.txt").write_text("content")

#         files = SysUtil.list_files(large_dir)
#         assert len(files) == 10000

#         size = SysUtil.get_file_size(large_dir)
#         assert size == 7 * 10000  # "content" is 7 bytes, 10000 files

#     def test_save_to_file(self, tmp_path):
#         text = "Hello, World!"
#         directory = tmp_path / "test_dir"
#         filename = "test_file.txt"

#         file_path = SysUtil.save_to_file(
#             text, directory, filename, timestamp=False, random_hash_digits=0
#         )

#         assert file_path.exists()
#         assert file_path.read_text() == text
#         assert file_path == directory / filename

#     def test_save_to_file_with_timestamp(self, tmp_path):
#         text = "Hello, World!"
#         directory = tmp_path / "test_dir"
#         filename = "test_file.txt"

#         file_path = SysUtil.save_to_file(
#             text, directory, filename, timestamp=True
#         )

#         assert file_path.exists()
#         assert file_path.read_text() == text
#         assert file_path.name.startswith("test_file_")
#         assert file_path.name.endswith(".txt")

#     def test_save_to_file_with_random_hash(self, tmp_path):
#         text = "Hello, World!"
#         directory = tmp_path / "test_dir"
#         filename = "test_file.txt"

#         file_path = SysUtil.save_to_file(
#             text, directory, filename, timestamp=False, random_hash_digits=6
#         )

#         assert file_path.exists()
#         assert file_path.read_text() == text
#         assert (
#             len(file_path.stem) == len("test_file") + 1 + 6
#         )  # name + hyphen + hash
#         assert file_path.name.endswith(".txt")

#     def test_read_file(self, tmp_path):
#         text = "Hello, World!"
#         file_path = tmp_path / "test_file.txt"
#         file_path.write_text(text)

#         result = SysUtil.read_file(file_path)

#         assert result == text

#     def test_read_file_not_found(self, tmp_path):
#         non_existent_file = tmp_path / "non_existent.txt"

#         with pytest.raises(FileNotFoundError):
#             SysUtil.read_file(non_existent_file)

#     @pytest.mark.parametrize(
#         "machine,expected",
#         [
#             ("arm64", "arm64"),
#             ("aarch64", "arm64"),
#             ("x86_64", "x86_64"),
#             ("amd64", "x86_64"),
#             ("i386", "i386"),
#             ("powerpc", "powerpc"),
#         ],
#     )
#     def test_get_cpu_architecture(self, machine, expected):
#         with patch("platform.machine", return_value=machine):
#             assert SysUtil.get_cpu_architecture() == expected


# # File: tests/test_sys_util.py

# import importlib
# import subprocess
# from pathlib import Path
# from unittest.mock import MagicMock, patch


# class TestSysUtil:

#     def test_save_to_file(self, tmp_path):
#         text = "Hello, World!"
#         directory = tmp_path / "test_dir"
#         filename = "test_file.txt"

#         file_path = SysUtil.save_to_file(
#             text, directory, filename, timestamp=False, random_hash_digits=0
#         )

#         assert file_path.exists()
#         assert file_path.read_text() == text
#         assert file_path == directory / filename

#     def test_save_to_file_with_timestamp(self, tmp_path):
#         text = "Hello, World!"
#         directory = tmp_path / "test_dir"
#         filename = "test_file.txt"

#         file_path = SysUtil.save_to_file(
#             text, directory, filename, timestamp=True
#         )

#         assert file_path.exists()
#         assert file_path.read_text() == text
#         assert file_path.name.startswith("test_file_")
#         assert file_path.name.endswith(".txt")

#     def test_save_to_file_with_random_hash(self, tmp_path):
#         text = "Hello, World!"
#         directory = tmp_path / "test_dir"
#         filename = "test_file.txt"

#         file_path = SysUtil.save_to_file(
#             text, directory, filename, timestamp=False, random_hash_digits=6
#         )

#         assert file_path.exists()
#         assert file_path.read_text() == text
#         assert (
#             len(file_path.stem) == len("test_file") + 1 + 6
#         )  # name + hyphen + hash
#         assert file_path.name.endswith(".txt")

#     def test_read_file(self, tmp_path):
#         text = "Hello, World!"
#         file_path = tmp_path / "test_file.txt"
#         file_path.write_text(text)

#         result = SysUtil.read_file(file_path)

#         assert result == text

#     def test_read_file_not_found(self, tmp_path):
#         non_existent_file = tmp_path / "non_existent.txt"

#         with pytest.raises(FileNotFoundError):
#             SysUtil.read_file(non_existent_file)

#     @pytest.mark.parametrize(
#         "machine,expected",
#         [
#             ("arm64", "arm64"),
#             ("aarch64", "arm64"),
#             ("x86_64", "x86_64"),
#             ("amd64", "x86_64"),
#             ("i386", "i386"),
#             ("powerpc", "powerpc"),
#         ],
#     )
#     def test_get_cpu_architecture(self, machine, expected):
#         with patch("platform.machine", return_value=machine):
#             assert SysUtil.get_cpu_architecture() == expected

#     @patch("lion_core.sys_utils.SysUtil.import_module")  # Updated patch path
#     @patch("lion_core.sys_utils._run_pip_command")  # Updated patch path
#     def test_install_import_success(self, mock_run_pip, mock_import):
#         mock_import.side_effect = [ImportError, MagicMock()]

#         result = SysUtil.install_import("test_package")

#         assert mock_run_pip.called
#         assert mock_import.call_count == 2
#         assert result is not None

#     @patch("lion_core.sys_utils.SysUtil.import_module")  # Updated patch path
#     @patch("lion_core.sys_utils._run_pip_command")  # Updated patch path
#     def test_install_import_failure(self, mock_run_pip, mock_import):
#         mock_import.side_effect = ImportError
#         mock_run_pip.side_effect = subprocess.CalledProcessError(1, "pip")

#         with pytest.raises(ImportError):
#             SysUtil.install_import("test_package")

#     @patch("builtins.__import__")
#     def test_import_module_success(self, mock_import):
#         mock_module = MagicMock()
#         mock_module.TestClass = "TestClass"
#         mock_import.return_value = mock_module

#         result = SysUtil.import_module(
#             "test_package", "test_module", "TestClass"
#         )

#         assert result == "TestClass"
#         mock_import.assert_called_with(
#             "test_package.test_module", fromlist=["TestClass"]
#         )

#     @patch("importlib.import_module")
#     def test_import_module_failure(self, mock_import):
#         mock_import.side_effect = ImportError

#         with pytest.raises(ImportError):
#             SysUtil.import_module("non_existent_package")

#     @patch("importlib.util.find_spec")
#     def test_is_package_installed_true(self, mock_find_spec):
#         mock_find_spec.return_value = MagicMock()

#         assert SysUtil.is_package_installed("existing_package") is True

#     @patch("importlib.util.find_spec")
#     def test_is_package_installed_false(self, mock_find_spec):
#         mock_find_spec.return_value = None

#         assert SysUtil.is_package_installed("non_existent_package") is False

#     @patch(
#         "lion_core.sys_utils.SysUtil.is_package_installed"
#     )  # Updated patch path
#     @patch("lion_core.sys_utils.SysUtil.install_import")  # Updated patch path
#     @patch("lion_core.sys_utils.SysUtil.import_module")  # Updated patch path
#     def test_check_import_installed(
#         self, mock_import, mock_install, mock_is_installed
#     ):
#         mock_is_installed.return_value = True
#         mock_import.return_value = MagicMock()

#         result = SysUtil.check_import("existing_package")

#         assert result is not None
#         assert not mock_install.called

#     @patch(
#         "lion_core.sys_utils.SysUtil.is_package_installed"
#     )  # Updated patch path
#     @patch("lion_core.sys_utils.SysUtil.install_import")  # Updated patch path
#     def test_check_import_not_installed_attempt_install(
#         self, mock_install, mock_is_installed
#     ):
#         mock_is_installed.return_value = False
#         mock_install.return_value = MagicMock()

#         result = SysUtil.check_import("new_package", attempt_install=True)

#         assert result is not None
#         assert mock_install.called

#     @patch(
#         "lion_core.sys_utils.SysUtil.is_package_installed"
#     )  # Updated patch path
#     def test_check_import_not_installed_no_attempt(self, mock_is_installed):
#         mock_is_installed.return_value = False

#         with pytest.raises(ImportError):
#             SysUtil.check_import("new_package", attempt_install=False)

#     @patch("importlib.metadata.distributions")
#     def test_list_installed_packages(self, mock_distributions):
#         mock_dist1 = MagicMock()
#         mock_dist1.metadata = {"Name": "package1"}
#         mock_dist2 = MagicMock()
#         mock_dist2.metadata = {"Name": "package2"}
#         mock_distributions.return_value = [mock_dist1, mock_dist2]

#         result = SysUtil.list_installed_packages()

#         assert result == ["package1", "package2"]

#     @patch("importlib.metadata.distributions")
#     def test_list_installed_packages_error(self, mock_distributions):
#         mock_distributions.side_effect = Exception("Test error")

#         result = SysUtil.list_installed_packages()

#         assert result == []


# # File: tests/test_sys_utils.py

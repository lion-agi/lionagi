import pytest
import os
from pathlib import Path
from datetime import datetime
from lionagi.os.sys_utils import SysUtil

@pytest.fixture
def temp_dir(tmp_path):
    """Fixture to provide a temporary directory for testing."""
    return tmp_path

@pytest.fixture
def sample_file(temp_dir):
    """Fixture to create a sample file for testing."""
    file_path = temp_dir / "sample.txt"
    with open(file_path, "w") as f:
        f.write("Sample content")
    return file_path

def test_clear_path(temp_dir, sample_file):
    # Create some files and subdirectories
    (temp_dir / "file1.txt").touch()
    (temp_dir / "file2.txt").touch()
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").touch()

    # Test non-recursive clear
    SysUtil.clear_path(temp_dir, recursive=False)
    assert not (temp_dir / "file1.txt").exists()
    assert not (temp_dir / "file2.txt").exists()
    assert subdir.exists()
    assert (subdir / "file3.txt").exists()

    # Test recursive clear
    SysUtil.clear_path(temp_dir, recursive=True)
    assert not subdir.exists()
    assert not (subdir / "file3.txt").exists()

    # Test clear with exclusion
    (temp_dir / "keep.txt").touch()
    (temp_dir / "remove.txt").touch()
    SysUtil.clear_path(temp_dir, exclude=["keep.txt"])
    assert (temp_dir / "keep.txt").exists()
    assert not (temp_dir / "remove.txt").exists()

    # Test clearing non-existent directory
    with pytest.raises(FileNotFoundError):
        SysUtil.clear_path(temp_dir / "nonexistent")

def test_create_path(temp_dir):
    # Test basic path creation
    path = SysUtil.create_path(temp_dir, "test.txt")
    assert path.exists()
    assert path.name.startswith("test")
    assert path.suffix == ".txt"

    # Test with timestamp
    path = SysUtil.create_path(temp_dir, "test.txt", timestamp=True)
    assert len(path.stem) > len("test")

    # Test with random hash
    path = SysUtil.create_path(temp_dir, "test.txt", random_hash_digits=5)
    assert len(path.stem) > len("test")

    # Test existing file with file_exist_ok=False
    existing_path = temp_dir / "existing.txt"
    existing_path.touch()
    new_path = SysUtil.create_path(temp_dir, "existing.txt", file_exist_ok=False)
    assert new_path != existing_path
    assert new_path.exists()

    # Test invalid filename
    with pytest.raises(ValueError):
        SysUtil.create_path(temp_dir, "invalid/filename.txt")

def test_split_path():
    path = Path("/home/user/documents/file.txt")
    directory, filename = SysUtil.split_path(path)
    assert directory == Path("/home/user/documents")
    assert filename == "file.txt"

def test_list_files(temp_dir):
    # Create some files and subdirectories
    (temp_dir / "file1.txt").touch()
    (temp_dir / "file2.py").touch()
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").touch()

    # Test non-recursive listing
    files = SysUtil.list_files(temp_dir)
    assert len(files) == 2
    assert set(f.name for f in files) == {"file1.txt", "file2.py"}

    # Test recursive listing
    files = SysUtil.list_files(temp_dir, recursive=True)
    assert len(files) == 3
    assert set(f.name for f in files) == {"file1.txt", "file2.py", "file3.txt"}

    # Test listing with extension filter
    files = SysUtil.list_files(temp_dir, extension="txt", recursive=True)
    assert len(files) == 2
    assert set(f.name for f in files) == {"file1.txt", "file3.txt"}

    # Test listing non-existent directory
    with pytest.raises(NotADirectoryError):
        SysUtil.list_files(temp_dir / "nonexistent")

def test_copy_file(temp_dir, sample_file):
    dest_file = temp_dir / "dest.txt"

    # Test basic copy
    SysUtil.copy_file(sample_file, dest_file)
    assert dest_file.exists()
    assert dest_file.read_text() == "Sample content"

    # Test copy with overwrite
    with open(sample_file, "w") as f:
        f.write("New content")
    SysUtil.copy_file(sample_file, dest_file, overwrite=True)
    assert dest_file.read_text() == "New content"

    # Test copy without overwrite (should raise an error)
    with pytest.raises(FileExistsError):
        SysUtil.copy_file(sample_file, dest_file, overwrite=False)

    # Test copying non-existent file
    with pytest.raises(FileNotFoundError):
        SysUtil.copy_file(temp_dir / "nonexistent.txt", dest_file)

def test_move_file(temp_dir, sample_file):
    dest_file = temp_dir / "moved.txt"

    # Test basic move
    SysUtil.move_file(sample_file, dest_file)
    assert dest_file.exists()
    assert not sample_file.exists()
    assert dest_file.read_text() == "Sample content"

    # Test move with overwrite
    sample_file.write_text("New content")
    SysUtil.move_file(sample_file, dest_file, overwrite=True)
    assert dest_file.read_text() == "New content"

    # Test move without overwrite (should raise an error)
    sample_file.write_text("Another content")
    with pytest.raises(FileExistsError):
        SysUtil.move_file(sample_file, dest_file, overwrite=False)

    # Test moving non-existent file
    with pytest.raises(FileNotFoundError):
        SysUtil.move_file(temp_dir / "nonexistent.txt", dest_file)

def test_get_file_info(temp_dir, sample_file):
    # Test file info
    info = SysUtil.get_file_info(sample_file)
    assert info["type"] == "file"
    assert info["size"] == len("Sample content")
    assert "last_modified" in info
    assert "permissions" in info
    assert "md5" in info

    # Test directory info
    dir_info = SysUtil.get_file_info(temp_dir)
    assert dir_info["type"] == "directory"
    assert "size" in dir_info
    assert "last_modified" in dir_info
    assert "permissions" in dir_info
    assert "md5" not in dir_info

    # Test non-existent path
    with pytest.raises(FileNotFoundError):
        SysUtil.get_file_info(temp_dir / "nonexistent")

def test_get_file_size(temp_dir, sample_file):
    # Test file size
    assert SysUtil.get_file_size(sample_file) == len("Sample content")

    # Test directory size
    (temp_dir / "file1.txt").write_text("Content 1")
    (temp_dir / "file2.txt").write_text("Content 2")
    assert SysUtil.get_file_size(temp_dir) == len("Content 1") + len("Content 2")

    # Test non-existent path
    with pytest.raises(FileNotFoundError):
        SysUtil.get_file_size(temp_dir / "nonexistent")

def test_save_to_file(temp_dir):
    # Test saving string content
    file_path = SysUtil.save_to_file("Test content", temp_dir, "test.txt")
    assert file_path.exists()
    assert file_path.read_text() == "Test content"

    # Test saving binary content
    binary_content = b"Binary content"
    file_path = SysUtil.save_to_file(binary_content, temp_dir, "binary.bin", mode="wb", encoding=None)
    assert file_path.exists()
    assert file_path.read_bytes() == binary_content

    # Test saving with timestamp
    file_path = SysUtil.save_to_file("Timestamped content", temp_dir, "timestamped.txt", timestamp=True)
    assert file_path.exists()
    assert file_path.stem.startswith("timestamped_")

    # Test saving to non-existent directory
    with pytest.raises(OSError):
        SysUtil.save_to_file("Content", temp_dir / "nonexistent", "test.txt")

def test_read_file(temp_dir):
    # Test reading text file
    text_file = temp_dir / "text.txt"
    text_file.write_text("Test content")
    assert SysUtil.read_file(text_file) == "Test content"

    # Test reading binary file
    binary_file = temp_dir / "binary.bin"
    binary_content = b"Binary content"
    binary_file.write_bytes(binary_content)
    assert SysUtil.read_file(binary_file, mode="rb", encoding=None) == binary_content

    # Test reading non-existent file
    with pytest.raises(FileNotFoundError):
        SysUtil.read_file(temp_dir / "nonexistent.txt")

    # Test reading file without permission (simulated)
    no_perm_file = temp_dir / "no_perm.txt"
    no_perm_file.touch()
    os.chmod(no_perm_file, 0o000)
    with pytest.raises(PermissionError):
        SysUtil.read_file(no_perm_file)
    os.chmod(no_perm_file, 0o644)  # Reset permissions for cleanup
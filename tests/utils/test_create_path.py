import uuid
from pathlib import Path

import pytest

from lionagi.utils.create_path import create_path


def test_basic_filename_with_extension(tmp_path):
    p = create_path(tmp_path, "test.txt")
    assert p.name == "test.txt"
    assert p.suffix == ".txt"
    assert p.parent == tmp_path


def test_no_extension_raises(tmp_path):
    with pytest.raises(ValueError):
        create_path(tmp_path, "filename")


def test_timestamp_suffix(tmp_path):
    p = create_path(tmp_path, "data.log", timestamp=True)
    # timestamp in default format: YYYYmmddHHMMSS
    # Just check that suffix is there, not exact time
    assert p.suffix == ".log"
    assert "_" in p.stem
    # The part after underscore should be a 14 digit timestamp
    parts = p.stem.rsplit("_", 1)
    assert len(parts) == 2
    ts_str = parts[1]
    assert len(ts_str) == 14


def test_timestamp_prefix(tmp_path):
    p = create_path(tmp_path, "data.log", timestamp=True, time_prefix=True)
    parts = p.stem.split("_", 1)
    assert len(parts) == 2
    ts_str = parts[0]
    assert len(ts_str) == 14  # default timestamp length
    # ensure after timestamp is 'data'
    assert parts[1] == "data"


def test_custom_timestamp_format(tmp_path):
    p = create_path(
        tmp_path, "data.json", timestamp=True, timestamp_format="%Y-%m-%d"
    )
    # format %Y-%m-%d => length 10
    parts = p.stem.rsplit("_", 1)
    assert len(parts) == 2
    ts_str = parts[1]
    assert len(ts_str) == 10
    assert ts_str.count("-") == 2


def test_random_hash_digits(tmp_path):
    p = create_path(tmp_path, "report.md", random_hash_digits=8)
    # Should have - followed by 8 hex chars
    parts = p.stem.rsplit("-", 1)
    assert len(parts) == 2
    hash_part = parts[1]
    assert len(hash_part) == 8
    int(hash_part, 16)  # ensure hex


def test_timestamp_and_hash(tmp_path):
    p = create_path(tmp_path, "log.txt", timestamp=True, random_hash_digits=4)
    # name might be: log_YYYYmmddHHMMSS-xxxx.txt
    # Check structure
    base = p.stem
    # Should have one underscore separating name and timestamp, and then a dash for hash
    # log_YYYYmmddHHMMSS-xxxx
    assert "_" in base and "-" in base


def test_overwrite_file_exist_ok_false(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("already here")
    with pytest.raises(FileExistsError):
        create_path(tmp_path, "file.txt", file_exist_ok=False)


def test_overwrite_file_exist_ok_true(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("already here")
    p = create_path(tmp_path, "file.txt", file_exist_ok=True)
    assert p == f


def test_no_directory_separators_in_filename(tmp_path):
    with pytest.raises(ValueError):
        create_path(tmp_path, "bad/name.txt")


def test_custom_extension(tmp_path):
    p = create_path(tmp_path, "myfile", extension="csv")
    assert p.name == "myfile.csv"


def test_dir_exist_ok_false(tmp_path):
    new_dir = tmp_path / "sub"
    new_dir.mkdir()
    # If dir_exist_ok=False and directory exists, it should still not fail
    # because we do not raise in directory creation if exist_ok is True by default
    # Let's set dir_exist_ok=False and check if error is raised.
    # The code currently sets exist_ok=dir_exist_ok in mkdir call
    # If dir_exist_ok=False and directory exists, it will raise FileExistsError
    with pytest.raises(FileExistsError):
        create_path(new_dir, "data.txt", dir_exist_ok=False)


def test_dir_exist_ok_true(tmp_path):
    new_dir = tmp_path / "sub"
    new_dir.mkdir()
    # With dir_exist_ok=True, no error
    p = create_path(new_dir, "data.txt", dir_exist_ok=True)
    assert p.parent == new_dir

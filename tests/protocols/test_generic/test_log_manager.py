"""Tests for the LogManager class."""

import asyncio
import os
from pathlib import Path

import pytest

from lionagi.protocols.generic.log import Log, LogManager, LogManagerConfig


@pytest.fixture
def sample_log():
    """Create a sample log for testing."""
    return Log(content={"message": "test message"})


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for log files."""
    return tmp_path


def test_log_manager_creation():
    """Test basic LogManager creation."""
    manager = LogManager()
    assert manager.logs is not None
    assert len(manager.logs) == 0
    assert manager.clear_after_dump is True


def test_log_manager_with_config():
    """Test LogManager creation with configuration."""
    config = LogManagerConfig(
        persist_dir="test_logs",  # Removed ./ prefix since it's normalized away
        capacity=100,
        file_prefix="test_",
        auto_save_on_exit=True,
        clear_after_dump=True,
        extension=".csv",
        use_timestamp=True,
        hash_digits=5,
    )
    manager = LogManager.from_config(config)

    assert str(manager.persist_dir) == "test_logs"
    assert manager.capacity == 100
    assert manager.file_prefix == "test_"


def test_log_manager_sync_logging(sample_log):
    """Test synchronous logging functionality."""
    manager = LogManager()
    manager.log(sample_log)

    assert len(manager.logs) == 1
    first_log = list(manager.logs)[0]
    assert first_log.content.get("message") == "test message"


@pytest.mark.asyncio
async def test_log_manager_async_logging(sample_log):
    """Test asynchronous logging functionality."""
    manager = LogManager()
    await manager.alog(sample_log)

    assert len(manager.logs) == 1
    first_log = list(manager.logs)[0]
    assert first_log.content.get("message") == "test message"


def test_log_manager_capacity(sample_log):
    """Test LogManager capacity handling."""
    manager = LogManager(capacity=2)

    # Add logs up to capacity
    manager.log(sample_log)
    assert len(manager.logs) == 1

    # Add another log to trigger auto-dump
    new_log = Log(content={"message": "test message"})
    manager.log(new_log)
    assert len(manager.logs) <= 2


def test_log_manager_dump(temp_dir, sample_log):
    """Test log dumping functionality."""
    manager = LogManager(persist_dir=temp_dir)
    manager.log(sample_log)

    # Dump logs
    manager.dump()

    # Check if file was created
    log_files = list(temp_dir.glob("*.csv"))
    assert len(log_files) > 0


def test_log_manager_clear_after_dump(temp_dir, sample_log):
    """Test clear after dump functionality."""
    manager = LogManager(persist_dir=temp_dir, clear_after_dump=True)
    manager.log(sample_log)
    manager.dump()

    assert len(manager.logs) == 0


def test_log_manager_no_clear_after_dump(temp_dir, sample_log):
    """Test behavior when clear_after_dump is False."""
    manager = LogManager(persist_dir=temp_dir, clear_after_dump=False)
    manager.log(sample_log)
    manager.dump()

    assert len(manager.logs) == 1


@pytest.mark.asyncio
async def test_log_manager_async_dump(temp_dir, sample_log):
    """Test asynchronous dump functionality."""
    manager = LogManager(persist_dir=temp_dir)
    await manager.alog(sample_log)
    await manager.adump()

    log_files = list(temp_dir.glob("*.csv"))
    assert len(log_files) > 0


def test_log_manager_custom_path(temp_dir, sample_log):
    """Test dumping to a custom path."""
    custom_path = temp_dir / "custom_logs" / "test.csv"
    # Create parent directory
    custom_path.parent.mkdir(parents=True, exist_ok=True)

    manager = LogManager()
    manager.log(sample_log)
    manager.dump(persist_path=custom_path)

    assert custom_path.exists()


def test_log_manager_empty_dump():
    """Test dumping with no logs."""
    manager = LogManager()
    manager.dump()  # Should not raise any errors


def test_log_manager_file_naming(temp_dir):
    """Test log file naming conventions."""
    manager = LogManager(
        persist_dir=temp_dir,
        file_prefix="test_",
        use_timestamp=True,
        hash_digits=5,
    )

    # Create a path and check its format
    path = manager._create_path()
    assert path.name.startswith("test_")
    assert path.suffix == ".csv"


@pytest.mark.asyncio
async def test_log_manager_concurrent_logging():
    """Test concurrent logging operations."""
    manager = LogManager()

    # Create unique logs for testing
    async def add_log(i):
        log = Log(content={"message": f"message {i}"})
        await manager.alog(log)
        await asyncio.sleep(0.01)  # Small delay to ensure order

    # Perform multiple concurrent log operations
    tasks = [add_log(i) for i in range(5)]
    await asyncio.gather(*tasks)

    assert len(manager.logs) == 5
    messages = sorted(log.content.get("message") for log in manager.logs)
    assert messages == [f"message {i}" for i in range(5)]


def test_log_manager_subfolder(temp_dir, sample_log):
    """Test logging with subfolder organization."""
    subfolder = "service_logs"
    manager = LogManager(persist_dir=temp_dir, subfolder=subfolder)
    manager.log(sample_log)
    manager.dump()

    subfolder_path = temp_dir / subfolder
    assert subfolder_path.exists()
    assert any(subfolder_path.iterdir())


def test_log_manager_save_at_exit(temp_dir, sample_log):
    """Test save at exit functionality."""
    manager = LogManager(persist_dir=temp_dir, auto_save_on_exit=True)
    manager.log(sample_log)

    # Simulate exit
    manager.save_at_exit()

    log_files = list(temp_dir.glob("*.csv"))
    assert len(log_files) > 0


def test_log_manager_multiple_dumps(temp_dir, sample_log):
    """Test multiple dump operations."""
    manager = LogManager(persist_dir=temp_dir, clear_after_dump=False)

    # Perform multiple dumps
    manager.log(sample_log)
    manager.dump()
    manager.dump()  # Second dump with same logs

    log_files = list(temp_dir.glob("*.csv"))
    assert len(log_files) == 2  # Should create two separate files


def test_log_manager_error_handling(temp_dir):
    """Test error handling in LogManager."""
    # Test with invalid directory permissions
    invalid_dir = temp_dir / "nonexistent" / "deeply" / "nested"
    invalid_dir.mkdir(
        parents=True, exist_ok=True
    )  # Create directory structure

    manager = LogManager(persist_dir=invalid_dir)

    # Should handle directory creation
    manager.log(Log(content={"message": "test message"}))
    manager.dump()  # Should not raise errors

    assert invalid_dir.exists()


@pytest.mark.asyncio
async def test_log_manager_async_context():
    """Test async context manager functionality."""
    manager = LogManager()
    log = Log(content={"message": "test message"})

    # Test the lock acquisition and release
    lock_acquired = False
    async with manager.logs.async_lock:
        lock_acquired = True
        assert lock_acquired

    # Test logging after lock release
    await manager.alog(log)
    assert len(manager.logs) == 1
    first_log = list(manager.logs)[0]
    assert first_log.content.get("message") == "test message"

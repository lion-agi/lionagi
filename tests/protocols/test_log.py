"""Tests for protocol Log and LogManager system."""

import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict

from lionagi.protocols.base import IDType
from lionagi.protocols.log import Log, LogManager, LogParams
from lionagi.protocols.models import BaseAutoModel


class MockContent(BaseModel):
    """Mock content for testing."""

    message: str
    level: str

    model_config = ConfigDict(
        validate_default=True, extra="forbid", frozen=True
    )


class MockComplexContent(BaseAutoModel):
    """Mock content with nested structure."""

    data: dict[str, Any]
    metadata: dict[str, Any]


@pytest.fixture
def mock_content():
    """Create mock content for testing."""
    return MockContent(message="test message", level="INFO")


@pytest.fixture
def mock_complex_content():
    """Create mock complex content for testing."""
    return MockComplexContent(
        data={"key": "value"}, metadata={"source": "test"}
    )


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for log files."""
    return tmp_path


@pytest.fixture
async def log_manager(temp_dir) -> AsyncGenerator[LogManager, None]:
    """Create a LogManager with proper cleanup."""
    params = LogParams(
        persist_dir=str(temp_dir),
        auto_save_on_exit=False,  # Disable auto-save to prevent shutdown errors
    )
    manager = LogManager(params=params)
    yield manager

    # Cleanup
    if manager.has_logs():
        try:
            await manager.dump(clear=True)
        except Exception:
            pass  # Ignore cleanup errors


def test_log_with_dict():
    """Test Log creation with dictionary content."""
    content = {"message": "test", "level": "INFO"}
    log = Log(content=content)
    assert log.content == content
    assert isinstance(log.id, IDType)
    assert isinstance(str(log.id), str)
    assert isinstance(log.created_timestamp, float)


def test_log_with_pydantic_model(mock_content):
    """Test Log creation with Pydantic model content."""
    log = Log(content=mock_content)
    expected_content = mock_content.model_dump()
    assert log.content == expected_content


def test_log_with_complex_content(mock_complex_content):
    """Test Log creation with complex nested content."""
    log = Log(content=mock_complex_content)
    assert "data" in log.content
    assert "metadata" in log.content
    assert log.content["data"] == {"key": "value"}
    assert log.content["metadata"] == {"source": "test"}


def test_log_params_defaults():
    """Test LogParams default values."""
    params = LogParams()
    assert params.persist_dir == "./logs"
    assert params.filename == "logs"
    assert params.capacity is None
    assert params.auto_save_on_exit is True
    assert params.clear_after_dump is True


def test_log_params_custom():
    """Test LogParams with custom values."""
    params = LogParams(
        persist_dir="custom/logs",
        filename="app",
        capacity=100,
        auto_save_on_exit=False,
        clear_after_dump=False,
    )
    assert params.persist_dir == "custom/logs"
    assert params.filename == "app"
    assert params.capacity == 100
    assert not params.auto_save_on_exit
    assert not params.clear_after_dump


def test_log_params_filename_generation(temp_dir):
    """Test LogParams filename generation."""
    params = LogParams(persist_dir=str(temp_dir))
    path = params.generate_filename()

    # Check path components
    assert path.parent == temp_dir
    assert path.suffix == ".json"

    # Check filename format
    parts = path.stem.split("_")
    assert len(parts) == 3  # name_timestamp_hash
    assert len(parts[2]) == 6  # Random hash length

    # Verify directory creation
    assert temp_dir.exists()


@pytest.mark.asyncio
async def test_log_manager_initialization(log_manager):
    """Test LogManager initialization."""
    assert isinstance(log_manager.params, LogParams)
    assert len(log_manager.logs) == 0
    assert log_manager.has_logs() is False


@pytest.mark.asyncio
async def test_log_manager_basic_operations(log_manager):
    """Test basic LogManager operations."""
    log = Log(content={"message": "test"})

    # Test logging
    await log_manager.log(log)
    assert log_manager.has_logs()
    assert len(log_manager.logs) == 1

    # Verify stored log
    stored_log = list(log_manager.logs)[0]
    assert stored_log.content["message"] == "test"
    assert isinstance(stored_log.id, IDType)
    assert isinstance(str(stored_log.id), str)


@pytest.mark.asyncio
async def test_log_manager_capacity_management(temp_dir):
    """Test LogManager capacity handling."""
    params = LogParams(
        capacity=2, persist_dir=str(temp_dir), auto_save_on_exit=False
    )
    manager = LogManager(params=params)

    try:
        # Add logs up to capacity
        for i in range(3):
            await manager.log(Log(content={"message": f"log {i}"}))
            await asyncio.sleep(0.01)  # Allow for async operations

        # Should auto-dump when capacity exceeded
        assert len(manager.logs) <= 2
    finally:
        # Cleanup
        if manager.has_logs():
            await manager.dump(clear=True)


@pytest.mark.asyncio
async def test_log_manager_dump_operation(log_manager):
    """Test LogManager dump operation."""
    # Add some logs
    await log_manager.log(Log(content={"message": "test 1"}))
    await log_manager.log(Log(content={"message": "test 2"}))

    # Dump logs
    await log_manager.dump()

    # Verify file creation and content
    log_files = list(Path(log_manager.params.persist_dir).glob("*.json"))
    assert len(log_files) == 1

    with open(log_files[0]) as f:
        data = json.load(f)
        assert len(data) == 2
        assert data[0]["content"]["message"] == "test 1"
        assert data[1]["content"]["message"] == "test 2"


@pytest.mark.asyncio
async def test_log_manager_clear_after_dump(temp_dir):
    """Test clear after dump behavior."""
    # Test with clear_after_dump=True
    params1 = LogParams(
        persist_dir=str(temp_dir),
        clear_after_dump=True,
        auto_save_on_exit=False,
    )
    manager1 = LogManager(params=params1)
    await manager1.log(Log(content={"message": "test"}))
    await manager1.dump()
    assert len(manager1.logs) == 0

    # Test with clear_after_dump=False
    params2 = LogParams(
        persist_dir=str(temp_dir),
        clear_after_dump=False,
        auto_save_on_exit=False,
    )
    manager2 = LogManager(params=params2)
    await manager2.log(Log(content={"message": "test"}))
    await manager2.dump()
    assert len(manager2.logs) == 1

    # Cleanup
    await manager2.dump(clear=True)


@pytest.mark.asyncio
async def test_log_manager_concurrent_access(log_manager):
    """Test concurrent access to LogManager."""

    async def add_logs(task_id: int, count: int):
        for i in range(count):
            await log_manager.log(
                Log(
                    content={
                        "message": f"task_{task_id}_log_{i}",
                        "task_id": task_id,
                    }
                )
            )
            await asyncio.sleep(0.01)

    # Run multiple concurrent logging operations
    await asyncio.gather(add_logs(0, 5), add_logs(1, 5), add_logs(2, 5))

    # Verify all logs were added
    assert len(log_manager.logs) == 15

    # Each message should be unique due to task_id prefix
    messages = {log.content["message"] for log in log_manager.logs}
    assert len(messages) == 15

    # Verify we have logs from all tasks
    task_ids = {log.content["task_id"] for log in log_manager.logs}
    assert task_ids == {0, 1, 2}


@pytest.mark.asyncio
async def test_log_manager_custom_path_dump(log_manager, temp_dir):
    """Test dumping to a custom path."""
    custom_path = temp_dir / "custom.json"

    await log_manager.log(Log(content={"message": "test"}))
    await log_manager.dump(persist_path=custom_path)

    assert custom_path.exists()
    with open(custom_path) as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["content"]["message"] == "test"

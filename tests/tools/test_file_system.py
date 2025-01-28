"""
Comprehensive tests for enhanced file system tools.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator

import pytest
from pydantic import ValidationError

from lionagi.tools.file import (
    ExtensionPolicy,
    FileManager,
    FileSystemError,
    ManagerConfig,
    PathConstraintError,
    PathConstraints,
    ReaderTool,
    SymlinkPolicy,
    WriterTool,
)

# Fixtures


@pytest.fixture
async def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
async def manager(temp_dir):
    """Create configured file manager."""
    config = ManagerConfig(
        state_ttl=60,
        cleanup_interval=30,
        persist_path=str(temp_dir / "states.json"),
    )
    constraints = PathConstraints(
        allowed_paths=[temp_dir],
        symlink_policy=SymlinkPolicy.INTERNAL,
        extension_policy=ExtensionPolicy.ALLOW_LISTED,
        allowed_extensions=["txt", "md"],
        max_file_size=1024 * 1024,  # 1MB
    )
    async with FileManager(config, constraints) as manager:
        yield manager


@pytest.fixture
def reader(manager):
    """Create reader tool."""
    return ReaderTool(manager)


@pytest.fixture
def writer(manager):
    """Create writer tool."""
    return WriterTool(manager)


# Test Path Validation


async def test_path_constraints(manager, temp_dir):
    """Test path validation and constraints."""
    # Valid path
    valid_path = temp_dir / "test.txt"
    resolved = await manager.validate_operation(valid_path, "read")
    assert resolved == valid_path.resolve()

    # Invalid extension
    invalid_ext = temp_dir / "test.exe"
    with pytest.raises(PathConstraintError) as exc:
        await manager.validate_operation(invalid_ext, "read")
    assert "extension not allowed" in str(exc.value)

    # Outside allowed paths
    outside_path = Path("/tmp/test.txt")
    with pytest.raises(PathConstraintError) as exc:
        await manager.validate_operation(outside_path, "read")
    assert "not under any allowed root" in str(exc.value)


async def test_symlink_policies(manager, temp_dir):
    """Test symlink handling policies."""
    # Create test file and symlink
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")

    symlink = temp_dir / "test_link.txt"
    symlink.symlink_to(test_file)

    # Test internal symlink (allowed)
    resolved = await manager.validate_operation(symlink, "read")
    assert resolved == symlink.resolve()

    # Test external symlink (blocked)
    external_file = Path("/tmp/external.txt")
    external_link = temp_dir / "external_link.txt"
    with pytest.raises(PathConstraintError):
        external_link.symlink_to(external_file)
        await manager.validate_operation(external_link, "read")


# Test Atomic Operations


async def test_atomic_write(writer, temp_dir):
    """Test atomic write operations."""
    test_file = temp_dir / "atomic.txt"
    content = "test content\n" * 1000  # Multi-line content

    # Write with atomic option
    response = await writer.handle_request(
        {
            "action": "write",
            "path": str(test_file),
            "content": content,
            "options": {"atomic": True},
        }
    )

    assert response.success
    assert test_file.read_text() == content

    # Verify no temp files remain
    temp_files = list(temp_dir.glob("*.tmp"))
    assert not temp_files


async def test_concurrent_writes(writer, temp_dir):
    """Test concurrent write operations."""
    test_file = temp_dir / "concurrent.txt"

    async def write_content(content: str):
        return await writer.handle_request(
            {
                "action": "write",
                "path": str(test_file),
                "content": content,
                "options": {"atomic": True},
            }
        )

    # Attempt concurrent writes
    tasks = [write_content(f"content {i}\n") for i in range(10)]

    results = await asyncio.gather(*tasks)
    assert all(r.success for r in results)

    # Verify file has valid content
    content = test_file.read_text()
    assert "content" in content
    assert len(content.splitlines()) == 1


# Test Chunked Operations


async def test_chunked_reading(reader, temp_dir):
    """Test chunked reading."""
    # Create large test file
    test_file = temp_dir / "large.txt"
    content = "test content\n" * 1000
    test_file.write_text(content)

    # Read in chunks
    response = await reader.handle_request(
        {
            "action": "read",
            "path": str(test_file),
            "options": {"chunk_size": 1024},
        }
    )

    assert response.success
    assert response.content == content


async def test_chunked_writing(writer, temp_dir):
    """Test chunked writing."""
    test_file = temp_dir / "chunked.txt"
    content = "test content\n" * 1000

    # Write in chunks
    response = await writer.handle_request(
        {
            "action": "write",
            "path": str(test_file),
            "content": content,
            "options": {"max_chunk_size": 1024},
        }
    )

    assert response.success
    assert test_file.read_text() == content


# Test State Management


async def test_state_persistence(manager, temp_dir):
    """Test state persistence and recovery."""
    # Create test files
    file1 = temp_dir / "state1.txt"
    file2 = temp_dir / "state2.txt"
    file1.write_text("test1")
    file2.write_text("test2")

    # Get states
    state1 = await manager.get_state(file1)
    state2 = await manager.get_state(file2)

    # Modify states
    state1.metadata["test"] = "value1"
    state2.metadata["test"] = "value2"

    # Persist and stop
    await manager.persist_states()
    await manager.stop()

    # Create new manager
    config = ManagerConfig(persist_path=str(temp_dir / "states.json"))
    new_manager = FileManager(config)
    await new_manager.start()

    # Verify states recovered
    recovered1 = await new_manager.get_state(file1)
    recovered2 = await new_manager.get_state(file2)

    assert recovered1.metadata["test"] == "value1"
    assert recovered2.metadata["test"] == "value2"


# Test Metadata and Caching


async def test_metadata_extraction(reader, temp_dir):
    """Test metadata extraction."""
    # Create markdown file with metadata
    test_file = temp_dir / "test.md"
    content = """---
title: Test Document
author: Test Author
---
# Content
Test content here
"""
    test_file.write_text(content)

    # Open with metadata extraction
    response = await reader.handle_request(
        {
            "action": "open",
            "path": str(test_file),
            "options": {"extract_metadata": True},
        }
    )

    assert response.success
    assert "title" in response.metadata
    assert response.metadata["title"] == "Test Document"


async def test_content_caching(reader, temp_dir):
    """Test content caching."""
    # Create test file
    test_file = temp_dir / "cache.txt"
    content = "test content\n" * 100
    test_file.write_text(content)

    # Open with caching
    response = await reader.handle_request(
        {"action": "open", "path": str(test_file), "options": {"cache": True}}
    )

    assert response.success
    assert response.cached

    # Read from cache
    read_response = await reader.handle_request(
        {"action": "read", "path": str(test_file)}
    )

    assert read_response.success
    assert read_response.content == content


# Test Error Handling


async def test_file_size_limits(writer, temp_dir):
    """Test file size limits."""
    test_file = temp_dir / "large.txt"
    content = "x" * (2 * 1024 * 1024)  # 2MB (over limit)

    # Attempt to write oversized file
    with pytest.raises(FileSystemError) as exc:
        await writer.handle_request(
            {"action": "write", "path": str(test_file), "content": content}
        )
    assert "size exceeds maximum" in str(exc.value)


async def test_invalid_operations(manager, temp_dir):
    """Test invalid operation handling."""
    test_file = temp_dir / "test.txt"

    # Test non-existent file
    with pytest.raises(FileSystemError):
        await manager.validate_operation(test_file, "read")

    # Test invalid extension
    invalid_file = temp_dir / "test.exe"
    with pytest.raises(PathConstraintError):
        await manager.validate_operation(invalid_file, "write")


# Test Cleanup


async def test_state_cleanup(manager, temp_dir):
    """Test state cleanup."""
    # Create test file
    test_file = temp_dir / "cleanup.txt"
    test_file.write_text("test")

    # Get state
    state = await manager.get_state(test_file)
    state.last_accessed = None  # Force expiration

    # Run cleanup
    await manager.cleanup()

    # Verify state removed
    new_state = await manager.get_state(test_file)
    assert new_state != state


# Test Concurrency


async def test_concurrent_access(manager, reader, writer, temp_dir):
    """Test concurrent file access."""
    test_file = temp_dir / "concurrent.txt"
    test_file.write_text("initial")

    async def read_file():
        return await reader.handle_request(
            {"action": "read", "path": str(test_file)}
        )

    async def write_file(content: str):
        return await writer.handle_request(
            {
                "action": "write",
                "path": str(test_file),
                "content": content,
                "options": {"atomic": True},
            }
        )

    # Run concurrent operations
    read_task = asyncio.create_task(read_file())
    write_task = asyncio.create_task(write_file("updated"))

    results = await asyncio.gather(read_task, write_task)
    assert all(r.success for r in results)

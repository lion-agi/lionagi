"""
Example usage of enhanced file system tools.
Demonstrates key features and best practices.
"""

import asyncio
import tempfile
from pathlib import Path

from lionagi.tools.file import (
    ExtensionPolicy,
    FileManager,
    ManagerConfig,
    PathConstraints,
    ReaderTool,
    SymlinkPolicy,
    WriterTool,
    get_default_constraints,
)


async def basic_usage():
    """Demonstrate basic file operations."""
    # Create temporary directory for example
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        # Initialize manager with default constraints
        constraints = get_default_constraints()
        constraints.allowed_paths.add(temp_dir)

        config = ManagerConfig(
            state_ttl=1800,  # 30 minutes
            persist_path=str(temp_dir / "states.json"),
        )

        async with FileManager(config, constraints) as manager:
            # Create tools
            reader = ReaderTool(manager)
            writer = WriterTool(manager)

            # Write file
            test_file = temp_dir / "test.txt"
            write_response = await writer.handle_request(
                {
                    "action": "write",
                    "path": str(test_file),
                    "content": "Hello, World!\n",
                    "options": {"atomic": True, "backup": True},
                }
            )
            print(f"Write response: {write_response}")

            # Read file
            read_response = await reader.handle_request(
                {
                    "action": "read",
                    "path": str(test_file),
                    "options": {"extract_metadata": True},
                }
            )
            print(f"Read response: {read_response}")


async def advanced_features():
    """Demonstrate advanced features."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        # Configure with specific constraints
        constraints = PathConstraints(
            allowed_paths=[temp_dir],
            symlink_policy=SymlinkPolicy.INTERNAL,
            extension_policy=ExtensionPolicy.ALLOW_LISTED,
            allowed_extensions=["txt", "md"],
            max_file_size=1024 * 1024,  # 1MB
            blocked_patterns=[r".*\.tmp$", r".*~$"],
        )

        config = ManagerConfig(
            state_ttl=1800,
            cleanup_interval=300,
            persist_path=str(temp_dir / "states.json"),
            shard_size=1000,
            connection_pool_size=5,
        )

        async with FileManager(config, constraints) as manager:
            reader = ReaderTool(manager)
            writer = WriterTool(manager)

            # Create markdown file with metadata
            doc_file = temp_dir / "document.md"
            doc_content = """---
title: Test Document
author: Test Author
---

# Test Document

This is a test document with metadata.
"""
            # Write with atomic operation
            await writer.handle_request(
                {
                    "action": "write",
                    "path": str(doc_file),
                    "content": doc_content,
                    "options": {"atomic": True, "backup": True},
                }
            )

            # Read with metadata extraction
            read_response = await reader.handle_request(
                {
                    "action": "open",
                    "path": str(doc_file),
                    "options": {"extract_metadata": True, "cache": True},
                }
            )
            print(f"Document metadata: {read_response.metadata}")

            # Demonstrate chunked writing
            large_file = temp_dir / "large.txt"
            large_content = "Test content\n" * 1000

            await writer.handle_request(
                {
                    "action": "write",
                    "path": str(large_file),
                    "content": large_content,
                    "options": {"max_chunk_size": 1024, "atomic": True},
                }
            )

            # Read in chunks
            read_response = await reader.handle_request(
                {
                    "action": "read",
                    "path": str(large_file),
                    "options": {"chunk_size": 1024},
                }
            )
            print(f"Read {len(read_response.content)} bytes")


async def concurrent_operations():
    """Demonstrate concurrent file operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        async with FileManager(
            constraints=get_default_constraints()
        ) as manager:
            writer = WriterTool(manager)
            reader = ReaderTool(manager)

            # Create test file
            test_file = temp_dir / "concurrent.txt"
            await writer.handle_request(
                {
                    "action": "write",
                    "path": str(test_file),
                    "content": "initial content\n",
                }
            )

            # Concurrent read/write tasks
            async def read_task():
                return await reader.handle_request(
                    {"action": "read", "path": str(test_file)}
                )

            async def write_task(content: str):
                return await writer.handle_request(
                    {
                        "action": "write",
                        "path": str(test_file),
                        "content": content,
                        "options": {"atomic": True},
                    }
                )

            # Run concurrent operations
            tasks = [
                read_task(),
                write_task("updated content 1\n"),
                read_task(),
                write_task("updated content 2\n"),
                read_task(),
            ]

            results = await asyncio.gather(*tasks)
            for i, result in enumerate(results):
                print(f"Task {i} result: {result}")


async def state_management():
    """Demonstrate state management and persistence."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        state_file = temp_dir / "states.json"

        # Create initial manager
        config = ManagerConfig(persist_path=str(state_file))

        async with FileManager(config) as manager:
            # Create some files with state
            test_file = temp_dir / "test.txt"
            await manager.validate_operation(test_file, "write")
            state = await manager.get_state(test_file)

            # Add custom metadata
            state.metadata.update({"created_by": "example", "version": "1.0"})

            # States are automatically persisted on exit

        # Create new manager and restore states
        async with FileManager(config) as new_manager:
            # Verify state restored
            state = await new_manager.get_state(test_file)
            print(f"Restored state metadata: {state.metadata}")


async def main():
    """Run all examples."""
    print("\n=== Basic Usage ===")
    await basic_usage()

    print("\n=== Advanced Features ===")
    await advanced_features()

    print("\n=== Concurrent Operations ===")
    await concurrent_operations()

    print("\n=== State Management ===")
    await state_management()


if __name__ == "__main__":
    asyncio.run(main())

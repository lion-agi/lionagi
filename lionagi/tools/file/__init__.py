"""
Enhanced file system tools with robust path validation, atomic operations,
and state management.

Features:
- Atomic file operations
- Path validation and constraints
- Chunked reading/writing
- State persistence
- Connection pooling
- Metadata extraction
"""

from typing import Dict, List, Optional, Type, Union

from .base_ import (
    FileAccessError,
    FileLockError,
    FileNotFoundError,
    FileOperation,
    FileRequest,
    FileResponse,
    FileSizeError,
    FileState,
    FileStats,
    FileSystemError,
    PathConstraintError,
)
from .constraints import ExtensionPolicy, PathConstraints, SymlinkPolicy
from .manager_ import FileManager, ManagerConfig
from .reader_ import (
    ReaderAction,
    ReaderOptions,
    ReaderRequest,
    ReaderResponse,
    ReaderTool,
)
from .writer import (
    WriterAction,
    WriterOptions,
    WriterRequest,
    WriterResponse,
    WriterTool,
)

__all__ = [
    # Base types
    "FileOperation",
    "FileRequest",
    "FileResponse",
    "FileState",
    "FileStats",
    # Error types
    "FileSystemError",
    "PathConstraintError",
    "FileNotFoundError",
    "FileAccessError",
    "FileSizeError",
    "FileLockError",
    # Constraints
    "PathConstraints",
    "SymlinkPolicy",
    "ExtensionPolicy",
    # Manager
    "FileManager",
    "ManagerConfig",
    # Reader
    "ReaderTool",
    "ReaderAction",
    "ReaderRequest",
    "ReaderResponse",
    "ReaderOptions",
    # Writer
    "WriterTool",
    "WriterAction",
    "WriterRequest",
    "WriterResponse",
    "WriterOptions",
]

# Version info
__version__ = "0.2.0"


async def create_manager(
    config: Optional[Union[ManagerConfig, dict]] = None,
    constraints: Optional[PathConstraints] = None,
) -> FileManager:
    """
    Create and initialize a FileManager instance.

    Args:
        config: Optional manager configuration
        constraints: Optional path constraints

    Returns:
        Initialized FileManager

    Example:
        ```python
        manager = await create_manager(
            config={"state_ttl": 1800},
            constraints=PathConstraints(
                allowed_paths=["/data"],
                symlink_policy="internal"
            )
        )
        ```
    """
    manager = FileManager(config, constraints)
    await manager.start()
    return manager


def get_default_constraints() -> PathConstraints:
    """
    Get default path constraints configuration.

    Returns:
        PathConstraints with safe defaults

    Example:
        ```python
        constraints = get_default_constraints()
        manager = FileManager(constraints=constraints)
        ```
    """
    return PathConstraints(
        symlink_policy=SymlinkPolicy.INTERNAL,
        extension_policy=ExtensionPolicy.ALLOW_LISTED,
        allowed_extensions=[
            "txt",
            "md",
            "py",
            "js",
            "json",
            "yaml",
            "yml",
            "ini",
            "cfg",
            "csv",
            "tsv",
            "html",
            "htm",
            "css",
            "log",
            "env",
        ],
        blocked_patterns=[
            r".*\.pyc$",
            r".*\.pyo$",
            r".*\.pyd$",
            r".*\.so$",
            r".*\.dll$",
            r".*\.exe$",
            r".*\.bin$",
            r".*~$",
            r"\.git/.*",
            r"\.svn/.*",
            r"__pycache__/.*",
        ],
        max_file_size=50 * 1024 * 1024,  # 50MB
        max_path_length=255,
    )


# Convenience aliases
Manager = FileManager
Reader = ReaderTool
Writer = WriterTool

"""
Base components for file system operations.
Provides core types, models, and error handling with enhanced security and validation.
"""

import asyncio
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, model_validator


class FileOperation(str, Enum):
    """
    Supported file operations with clear intent.
    """

    READ = "read"  # Read file content
    WRITE = "write"  # Write (overwrite) file content
    APPEND = "append"  # Append to existing file
    DELETE = "delete"  # Delete file
    CREATE = "create"  # Create new file
    MOVE = "move"  # Move/rename file
    COPY = "copy"  # Copy file
    STAT = "stat"  # Get file statistics


class FileSystemError(Exception):
    """Base exception for file operations."""

    def __init__(self, message: str, path: Optional[Path] = None):
        self.path = path
        super().__init__(f"{message} [{path}]" if path else message)


class PathConstraintError(FileSystemError):
    """
    Error when path validation fails.
    Includes which constraint failed and why.
    """

    def __init__(
        self,
        path: Path,
        reason: str,
        pattern: Optional[str] = None,
        constraint: Optional[str] = None,
    ):
        self.reason = reason
        self.pattern = pattern
        self.constraint = constraint
        msg = f"Path constraint error for {path}: {reason}"
        if pattern:
            msg += f" (matched pattern: {pattern})"
        if constraint:
            msg += f" (failed constraint: {constraint})"
        super().__init__(msg, path)


class FileNotFoundError(FileSystemError):
    """File not found with path context."""

    pass


class FileAccessError(FileSystemError):
    """Permission or access error with details."""

    pass


class FileSizeError(FileSystemError):
    """File size limit exceeded."""

    pass


class FileLockError(FileSystemError):
    """File locking error with state details."""

    def __init__(
        self,
        message: str,
        path: Path,
        mode: str,
        current_mode: Optional[str] = None,
    ):
        self.mode = mode
        self.current_mode = current_mode
        msg = f"{message} (requested mode: {mode}"
        if current_mode:
            msg += f", current mode: {current_mode})"
        else:
            msg += ")"
        super().__init__(msg, path)


class FileState:
    """
    Enhanced file state tracking with locking and reference counting.

    Attributes:
        lock: Async lock for state access
        ref_count: Number of active references
        mode: Current file mode ('r', 'w', 'a')
        in_use: Whether file is actively being used
        last_accessed: Last access timestamp
        metadata: Custom metadata dict
    """

    def __init__(self):
        self.lock = asyncio.Lock()
        self.ref_count: int = 0
        self.mode: Optional[str] = None
        self.in_use: bool = False
        self.last_accessed: Optional[datetime] = None
        self.metadata: Dict[str, Any] = {}
        self._temp_path: Optional[Path] = None

    async def acquire(self, mode: str) -> bool:
        """
        Attempt to acquire file access.

        Args:
            mode: Requested file mode ('r', 'w', 'a')

        Returns:
            bool: True if access granted

        Note:
            Multiple readers allowed
            Only one writer at a time
            No readers while writing
        """
        if self.in_use:
            if mode == "w" or self.mode == "w":
                return False
            if mode == "r" and self.mode == "r":
                # Allow multiple readers
                async with self.lock:
                    self.ref_count += 1
                    self.last_accessed = datetime.now()
                return True
            return False

        async with self.lock:
            self.ref_count = 1
            self.mode = mode
            self.in_use = True
            self.last_accessed = datetime.now()
        return True

    async def release(self):
        """Release file access and update state."""
        async with self.lock:
            self.ref_count -= 1
            if self.ref_count == 0:
                self.in_use = False
                self.mode = None
                # Cleanup temp file if exists
                if self._temp_path and self._temp_path.exists():
                    self._temp_path.unlink()
                self._temp_path = None

    def __enter__(self):
        raise TypeError("Use 'async with' instead")

    def __exit__(self, *args):
        raise TypeError("Use 'async with' instead")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Async context manager exit with cleanup."""
        await self.release()


class FileRequest(BaseModel):
    """
    Base request model for file operations.
    All file operation requests inherit from this.
    """

    operation: FileOperation = Field(..., description="Operation type")
    path: str = Field(..., description="Target file path")
    mode: str = Field("r", description="File mode (r/w/a)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Optional metadata"
    )

    @model_validator(mode="before")
    def validate_request(cls, values):
        """Validate operation and mode compatibility."""
        operation = values.get("operation")
        mode = values.get("mode", "r")

        if operation == FileOperation.READ and mode != "r":
            raise ValueError("Read operation requires mode 'r'")
        if operation in (
            FileOperation.WRITE,
            FileOperation.CREATE,
        ) and mode not in ("w", "a"):
            raise ValueError("Write/create operations require mode 'w' or 'a'")
        return values

    def resolve_path(self) -> Path:
        """Resolve path string to Path object."""
        return Path(self.path).resolve()


class FileResponse(BaseModel):
    """
    Base response model for file operations.
    All file operation responses inherit from this.
    """

    success: bool = Field(..., description="Operation success status")
    error: Optional[str] = Field(None, description="Error message if failed")
    path: Optional[str] = Field(None, description="Target file path")
    operation: Optional[FileOperation] = Field(
        None, description="Performed operation"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Operation metadata"
    )


class FileStats(BaseModel):
    """File statistics and metadata."""

    path: str = Field(..., description="File path")
    size: int = Field(..., description="File size in bytes")
    created: datetime = Field(..., description="Creation timestamp")
    modified: datetime = Field(..., description="Last modified timestamp")
    accessed: datetime = Field(..., description="Last accessed timestamp")
    is_file: bool = Field(..., description="True if regular file")
    is_dir: bool = Field(..., description="True if directory")
    is_symlink: bool = Field(..., description="True if symlink")
    mode: int = Field(..., description="File mode (permissions)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Custom metadata"
    )

    @classmethod
    def from_path(cls, path: Path) -> "FileStats":
        """Create FileStats from Path object."""
        stat = path.stat()
        return cls(
            path=str(path),
            size=stat.st_size,
            created=datetime.fromtimestamp(stat.st_ctime),
            modified=datetime.fromtimestamp(stat.st_mtime),
            accessed=datetime.fromtimestamp(stat.st_atime),
            is_file=path.is_file(),
            is_dir=path.is_dir(),
            is_symlink=path.is_symlink(),
            mode=stat.st_mode,
        )

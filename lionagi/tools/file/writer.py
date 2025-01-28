"""
Enhanced file writing operations with atomic writes and chunked I/O.
"""

import asyncio
import os
import tempfile
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union

import aiofiles
from pydantic import BaseModel, Field, model_validator

from ..base import LionTool
from .base_ import (
    FileOperation,
    FileRequest,
    FileResponse,
    FileSizeError,
    FileState,
    FileSystemError,
)


class WriterAction(str, Enum):
    """Writer operation types."""

    WRITE = "write"  # Write/overwrite file
    APPEND = "append"  # Append to file
    DELETE = "delete"  # Delete file
    MOVE = "move"  # Move/rename file
    COPY = "copy"  # Copy file


class WriterOptions(BaseModel):
    """
    Configuration options for write operations.

    Attributes:
        max_chunk_size: Maximum size for chunked writing
        atomic: Use atomic operations
        preserve_timestamps: Keep original timestamps
        create_parents: Create parent directories
        backup: Create backup before write
    """

    max_chunk_size: Optional[int] = Field(
        None, description="Maximum chunk size for writing", ge=0
    )
    atomic: bool = Field(True, description="Use atomic write operations")
    preserve_timestamps: bool = Field(
        False, description="Preserve original timestamps"
    )
    create_parents: bool = Field(
        True, description="Create parent directories if needed"
    )
    backup: bool = Field(False, description="Create backup before writing")
    encoding: str = Field("utf-8", description="File encoding")


class WriterRequest(FileRequest):
    """
    Request for write operations.

    Examples:
        Write file:
        ```python
        {
            "action": "write",
            "path": "path/to/file.txt",
            "content": "Hello World",
            "options": {
                "atomic": True,
                "backup": True
            }
        }
        ```

        Move file:
        ```python
        {
            "action": "move",
            "path": "source.txt",
            "destination": "dest.txt"
        }
        ```
    """

    action: WriterAction = Field(..., description="Write operation type")
    content: Optional[str] = Field(None, description="Content to write")
    destination: Optional[str] = Field(
        None, description="Destination for move/copy"
    )
    options: WriterOptions = Field(
        default_factory=WriterOptions, description="Write options"
    )

    @model_validator(mode="after")
    def validate_request(self) -> "WriterRequest":
        """Validate request fields based on action."""
        if self.action in (WriterAction.WRITE, WriterAction.APPEND):
            if not self.content:
                raise ValueError(f"{self.action} requires content")
        elif self.action in (WriterAction.MOVE, WriterAction.COPY):
            if not self.destination:
                raise ValueError(f"{self.action} requires destination")
        return self


class WriterResponse(FileResponse):
    """
    Response from write operations.

    Attributes:
        path: Path written to
        size: Bytes written
        backup_path: Path to backup if created
    """

    size: Optional[int] = Field(None, description="Bytes written")
    backup_path: Optional[str] = Field(None, description="Backup file path")


class WriterTool(LionTool):
    """
    Enhanced file writing tool with atomic operations and chunking.

    Features:
    - Atomic write operations
    - Chunked writing for large files
    - File backups
    - Timestamp preservation
    - Parent directory creation
    """

    is_lion_system_tool = True
    system_tool_name = "writer_tool"

    def __init__(self, file_manager):
        """Initialize with file manager."""
        super().__init__()
        self.file_manager = file_manager
        self._tool = None

    async def handle_request(self, request: WriterRequest) -> WriterResponse:
        """
        Handle write operation requests.

        Args:
            request: Write operation details

        Returns:
            Operation result
        """
        if isinstance(request, dict):
            request = WriterRequest(**request)

        try:
            # Validate path and get state
            path = await self.file_manager.validate_operation(
                request.path, operation=FileOperation.WRITE
            )

            state = await self.file_manager.get_state(path)

            # Execute operation
            if request.action in (WriterAction.WRITE, WriterAction.APPEND):
                return await self._write_file(
                    path,
                    request.content,
                    append=(request.action == WriterAction.APPEND),
                    options=request.options,
                    state=state,
                )
            elif request.action == WriterAction.DELETE:
                return await self._delete_file(path, state)
            elif request.action in (WriterAction.MOVE, WriterAction.COPY):
                dest = await self.file_manager.validate_operation(
                    request.destination, operation=FileOperation.WRITE
                )
                if request.action == WriterAction.MOVE:
                    return await self._move_file(
                        path, dest, request.options, state
                    )
                else:
                    return await self._copy_file(
                        path, dest, request.options, state
                    )

        except Exception as e:
            return WriterResponse(
                success=False,
                error=str(e),
                path=request.path,
                operation=request.action,
            )

    async def _write_file(
        self,
        path: Path,
        content: str,
        append: bool = False,
        options: WriterOptions = None,
        state: FileState = None,
    ) -> WriterResponse:
        """Write or append content to file."""
        if not options:
            options = WriterOptions()

        try:
            # Create parent directories
            if options.create_parents:
                path.parent.mkdir(parents=True, exist_ok=True)

            # Get original timestamps if preserving
            original_times = None
            if options.preserve_timestamps and path.exists():
                stat = path.stat()
                original_times = (stat.st_atime, stat.st_mtime)

            # Create backup if requested
            backup_path = None
            if options.backup and path.exists():
                backup_path = path.with_suffix(f"{path.suffix}.bak")
                await self._copy_file_content(path, backup_path)

            # Write content
            mode = "a" if append else "w"
            size = await self._write_content(
                path, content, mode=mode, options=options, state=state
            )

            # Restore timestamps if requested
            if options.preserve_timestamps and original_times:
                os.utime(path, original_times)

            return WriterResponse(
                success=True,
                path=str(path),
                operation=(
                    WriterAction.APPEND if append else WriterAction.WRITE
                ),
                size=size,
                backup_path=str(backup_path) if backup_path else None,
            )

        except Exception as e:
            # Cleanup any incomplete writes
            if state and state._temp_path and state._temp_path.exists():
                state._temp_path.unlink()
            raise FileSystemError(f"Write failed: {e}", path)

    async def _write_content(
        self,
        path: Path,
        content: str,
        mode: str,
        options: WriterOptions,
        state: FileState,
    ) -> int:
        """Write content with chunking and atomic options."""
        if not options.atomic:
            # Direct write
            async with aiofiles.open(
                path, mode=mode, encoding=options.encoding
            ) as f:
                if options.max_chunk_size:
                    size = 0
                    for i in range(0, len(content), options.max_chunk_size):
                        chunk = content[i : i + options.max_chunk_size]
                        await f.write(chunk)
                        size += len(chunk)
                else:
                    await f.write(content)
                    size = len(content)
                await f.flush()
                os.fsync(f.fileno())
            return size

        else:
            # Atomic write using temporary file
            temp_file = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding=options.encoding,
                    delete=False,
                    dir=path.parent,
                ) as temp_file:
                    if options.max_chunk_size:
                        size = 0
                        for i in range(
                            0, len(content), options.max_chunk_size
                        ):
                            chunk = content[i : i + options.max_chunk_size]
                            temp_file.write(chunk)
                            size += len(chunk)
                    else:
                        temp_file.write(content)
                        size = len(content)
                    temp_file.flush()
                    os.fsync(temp_file.fileno())

                # Store temp path in state for cleanup
                if state:
                    state._temp_path = Path(temp_file.name)

                # Atomic rename
                os.replace(temp_file.name, path)
                return size

            except Exception as e:
                # Cleanup temp file
                if temp_file and Path(temp_file.name).exists():
                    Path(temp_file.name).unlink()
                raise e

    async def _delete_file(
        self, path: Path, state: FileState = None
    ) -> WriterResponse:
        """Delete file with state cleanup."""
        try:
            if path.exists():
                path.unlink()
            return WriterResponse(
                success=True, path=str(path), operation=WriterAction.DELETE
            )
        except Exception as e:
            raise FileSystemError(f"Delete failed: {e}", path)

    async def _move_file(
        self,
        source: Path,
        dest: Path,
        options: WriterOptions,
        state: FileState = None,
    ) -> WriterResponse:
        """Move file with atomic option."""
        try:
            if options.create_parents:
                dest.parent.mkdir(parents=True, exist_ok=True)

            if options.atomic:
                # Copy then delete for atomic move
                await self._copy_file_content(source, dest)
                source.unlink()
            else:
                # Direct move
                source.rename(dest)

            return WriterResponse(
                success=True, path=str(dest), operation=WriterAction.MOVE
            )

        except Exception as e:
            raise FileSystemError(f"Move failed: {e}", source)

    async def _copy_file(
        self,
        source: Path,
        dest: Path,
        options: WriterOptions,
        state: FileState = None,
    ) -> WriterResponse:
        """Copy file with options."""
        try:
            if options.create_parents:
                dest.parent.mkdir(parents=True, exist_ok=True)

            await self._copy_file_content(source, dest)

            if options.preserve_timestamps:
                stat = source.stat()
                os.utime(dest, (stat.st_atime, stat.st_mtime))

            return WriterResponse(
                success=True, path=str(dest), operation=WriterAction.COPY
            )

        except Exception as e:
            raise FileSystemError(f"Copy failed: {e}", source)

    async def _copy_file_content(
        self, source: Path, dest: Path, chunk_size: int = 8192
    ) -> None:
        """Copy file contents in chunks."""
        async with (
            aiofiles.open(source, "rb") as sf,
            aiofiles.open(dest, "wb") as df,
        ):
            while chunk := await sf.read(chunk_size):
                await df.write(chunk)

    def to_tool(self):
        """Convert to Tool instance."""
        if self._tool is not None:
            return self._tool

        def writer_tool(**kwargs):
            """Tool for file write operations."""
            return self.handle_request(WriterRequest(**kwargs))

        if self.system_tool_name != "writer_tool":
            writer_tool.__name__ = self.system_tool_name

        from lionagi.operatives.action.tool import Tool

        self._tool = Tool(
            func_callable=writer_tool, request_options=WriterRequest
        )
        return self._tool

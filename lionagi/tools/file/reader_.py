"""
Enhanced file reading operations with chunked reading and streaming.
"""

import asyncio
import os
import tempfile
from enum import Enum
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Optional, Union

import aiofiles
from pydantic import BaseModel, Field, model_validator

from lionagi.libs.package.imports import check_import
from lionagi.operatives.action.tool import Tool
from lionagi.utils import to_num

from ..base import LionTool
from .base_ import (
    FileOperation,
    FileRequest,
    FileResponse,
    FileState,
    FileStats,
    FileSystemError,
)


class ReaderAction(str, Enum):
    """Reader operation types."""

    OPEN = "open"  # Open and prepare file for reading
    READ = "read"  # Read file content
    STREAM = "stream"  # Stream file content
    STAT = "stat"  # Get file statistics


class ReaderOptions(BaseModel):
    """
    Configuration options for read operations.

    Attributes:
        chunk_size: Size of chunks for reading
        cache: Whether to cache file content
        extract_metadata: Extract file metadata
        follow_symlinks: Follow symbolic links
    """

    chunk_size: int = Field(8192, description="Chunk size for reading", ge=0)
    cache: bool = Field(True, description="Cache file content")
    extract_metadata: bool = Field(True, description="Extract file metadata")
    follow_symlinks: bool = Field(False, description="Follow symbolic links")
    encoding: str = Field("utf-8", description="File encoding")


class ReaderRequest(FileRequest):
    """
    Request for read operations.

    Examples:
        Open file:
        ```python
        {
            "action": "open",
            "path": "path/to/file.txt",
            "options": {
                "cache": True,
                "extract_metadata": True
            }
        }
        ```

        Read chunks:
        ```python
        {
            "action": "read",
            "path": "path/to/file.txt",
            "start_offset": 0,
            "end_offset": 1000
        }
        ```
    """

    action: ReaderAction = Field(..., description="Read operation type")
    start_offset: Optional[int] = Field(
        None, description="Start offset for partial read", ge=0
    )
    end_offset: Optional[int] = Field(
        None, description="End offset for partial read", ge=0
    )
    options: ReaderOptions = Field(
        default_factory=ReaderOptions, description="Read options"
    )

    @model_validator(mode="before")
    def validate_offsets(cls, values):
        """Validate and convert offset values."""
        start = values.get("start_offset")
        end = values.get("end_offset")

        if start is not None:
            try:
                values["start_offset"] = to_num(start, num_type=int)
            except ValueError:
                values["start_offset"] = None

        if end is not None:
            try:
                values["end_offset"] = to_num(end, num_type=int)
            except ValueError:
                values["end_offset"] = None

        if start is not None and end is not None:
            if start > end:
                raise ValueError(
                    "start_offset cannot be greater than end_offset"
                )

        return values


class ReaderResponse(FileResponse):
    """
    Response from read operations.

    Attributes:
        content: File content if read
        stats: File statistics
        cached: Whether content is cached
    """

    content: Optional[str] = Field(None, description="File content")
    stats: Optional[FileStats] = Field(None, description="File statistics")
    cached: bool = Field(False, description="Content is cached")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Extracted metadata"
    )


class ReaderTool(LionTool):
    """
    Enhanced file reading tool with chunking and streaming.

    Features:
    - Chunked reading
    - Content streaming
    - Metadata extraction
    - Content caching
    - Statistics tracking
    """

    is_lion_system_tool = True
    system_tool_name = "reader_tool"

    # Import document converter
    DocumentConverter = check_import(
        "docling",
        module_name="document_converter",
        import_name="DocumentConverter",
    )

    def __init__(self, file_manager):
        """Initialize with file manager."""
        super().__init__()
        self.file_manager = file_manager
        self.converter = ReaderTool.DocumentConverter()
        self._tool = None

    async def handle_request(self, request: ReaderRequest) -> ReaderResponse:
        """
        Handle read operation requests.

        Args:
            request: Read operation details

        Returns:
            Operation result
        """
        if isinstance(request, dict):
            request = ReaderRequest(**request)

        try:
            # Validate path and get state
            path = await self.file_manager.validate_operation(
                request.path, operation=FileOperation.READ
            )

            state = await self.file_manager.get_state(path)

            # Execute operation
            if request.action == ReaderAction.OPEN:
                return await self._open_file(
                    path, options=request.options, state=state
                )
            elif request.action == ReaderAction.READ:
                return await self._read_file(
                    path,
                    request.start_offset,
                    request.end_offset,
                    options=request.options,
                    state=state,
                )
            elif request.action == ReaderAction.STREAM:
                return await self._stream_file(
                    path, options=request.options, state=state
                )
            elif request.action == ReaderAction.STAT:
                return await self._stat_file(
                    path, options=request.options, state=state
                )

        except Exception as e:
            return ReaderResponse(
                success=False,
                error=str(e),
                path=request.path,
                operation=request.action,
            )

    async def _open_file(
        self, path: Path, options: ReaderOptions, state: FileState
    ) -> ReaderResponse:
        """Open and prepare file for reading."""
        try:
            # Get file statistics
            stats = FileStats.from_path(path)

            # Extract metadata if requested
            metadata = {}
            if options.extract_metadata:
                try:
                    result = self.converter.convert(str(path))
                    metadata = result.metadata
                except Exception as e:
                    metadata["error"] = f"Metadata extraction failed: {e}"

            # Cache content if requested
            cached = False
            if options.cache:
                if not state._temp_path:
                    # Create temp file with content
                    temp_file = tempfile.NamedTemporaryFile(
                        delete=False, mode="w", encoding=options.encoding
                    )
                    async with aiofiles.open(
                        path, encoding=options.encoding
                    ) as src:
                        while chunk := await src.read(options.chunk_size):
                            temp_file.write(chunk)
                    temp_file.close()
                    state._temp_path = Path(temp_file.name)
                cached = True

            return ReaderResponse(
                success=True,
                path=str(path),
                operation=ReaderAction.OPEN,
                stats=stats,
                cached=cached,
                metadata=metadata,
            )

        except Exception as e:
            raise FileSystemError(f"Open failed: {e}", path)

    async def _read_file(
        self,
        path: Path,
        start: Optional[int],
        end: Optional[int],
        options: ReaderOptions,
        state: FileState,
    ) -> ReaderResponse:
        """Read file content with optional offsets."""
        try:
            stats = FileStats.from_path(path)
            file_size = stats.size

            # Validate and adjust offsets
            start = max(0, start if start is not None else 0)
            end = min(file_size, end if end is not None else file_size)

            if start >= end:
                return ReaderResponse(
                    success=True,
                    path=str(path),
                    operation=ReaderAction.READ,
                    content="",
                )

            # Read content
            content = []
            read_path = state._temp_path if state._temp_path else path

            async with aiofiles.open(
                read_path, encoding=options.encoding
            ) as f:
                await f.seek(start)
                remaining = end - start
                while remaining > 0:
                    chunk_size = min(remaining, options.chunk_size)
                    chunk = await f.read(chunk_size)
                    if not chunk:
                        break
                    content.append(chunk)
                    remaining -= len(chunk)

            return ReaderResponse(
                success=True,
                path=str(path),
                operation=ReaderAction.READ,
                content="".join(content),
                stats=stats,
            )

        except Exception as e:
            raise FileSystemError(f"Read failed: {e}", path)

    async def _stream_file(
        self, path: Path, options: ReaderOptions, state: FileState
    ) -> AsyncGenerator[str, None]:
        """Stream file content in chunks."""
        try:
            async with aiofiles.open(path, encoding=options.encoding) as f:
                while chunk := await f.read(options.chunk_size):
                    yield chunk

        except Exception as e:
            raise FileSystemError(f"Stream failed: {e}", path)

    async def _stat_file(
        self, path: Path, options: ReaderOptions, state: FileState
    ) -> ReaderResponse:
        """Get file statistics and metadata."""
        try:
            stats = FileStats.from_path(path)

            # Extract metadata if requested
            metadata = {}
            if options.extract_metadata:
                try:
                    result = self.converter.convert(str(path))
                    metadata = result.metadata
                except Exception as e:
                    metadata["error"] = f"Metadata extraction failed: {e}"

            return ReaderResponse(
                success=True,
                path=str(path),
                operation=ReaderAction.STAT,
                stats=stats,
                metadata=metadata,
            )

        except Exception as e:
            raise FileSystemError(f"Stat failed: {e}", path)

    def to_tool(self):
        """Convert to Tool instance."""
        if self._tool is not None:
            return self._tool

        def reader_tool(**kwargs):
            """Tool for file read operations."""
            return self.handle_request(ReaderRequest(**kwargs))

        if self.system_tool_name != "reader_tool":
            reader_tool.__name__ = self.system_tool_name

        self._tool = Tool(
            func_callable=reader_tool, request_options=ReaderRequest
        )
        return self._tool

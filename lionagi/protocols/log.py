# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Asynchronous log management system with thread-safe operations and file persistence.
Provides automatic log rotation, capacity management, and graceful shutdown handling.
Core features:
- Concurrent-safe log operations using async locks
- Configurable file persistence with rotation
- Automatic cleanup and exit handling
- Flexible log entry validation and formatting
"""

from __future__ import annotations

import asyncio
import atexit
import json
import logging
import random
import string
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

from lionagi.libs.parse import ToDictParams

from .models import BaseAutoModel
from .pile import Pile

__all__ = (
    "Log",
    "LogParams",
    "LogManager",
)


TO_LOGDICT = ToDictParams(
    use_model_dump=False,
    use_enum_values=True,
    suppress=True,
    recursive=True,
    recursive_python_only=False,
    max_recursive_depth=5,
)


class Log(BaseAutoModel):
    """
    Log entry model with automatic content validation and conversion.
    Handles both dictionary and object content by converting to a standardized format.

    Attributes:
        content: Dictionary containing log data. Objects with to_dict() method
                are automatically converted.
    """

    content: dict[str, Any] = Field(
        default_factory=dict, description="Main log content."
    )

    @field_validator("content", mode="before")
    def _validate_content(cls, value) -> None:
        if not isinstance(value, dict):
            if hasattr(value, "to_dict"):
                return value.to_dict()
            return TO_LOGDICT(value)
        return value


class LogParams(BaseModel):
    """
    Configuration for log management behavior and persistence.
    Controls file locations, capacity limits, and cleanup behavior.

    Attributes:
        persist_dir: Directory path for log files
        filename: Base name for log files before timestamp/hash
        capacity: Max logs before auto-dump (None for unlimited)
        auto_save_on_exit: Enable automatic save on program exit
        clear_after_dump: Clear logs after successful file dump
    """

    persist_dir: str = "./logs"
    filename: str = "logs"
    capacity: int | None = None
    auto_save_on_exit: bool = True
    clear_after_dump: bool = True

    def generate_filename(self) -> Path:
        """
        Creates unique log filename using timestamp and random hash.
        Ensures directory exists and generates collision-resistant names.
        Format: {filename}_{YYYYMMDDHHMMSS}_{random6chars}.json
        """
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_hash = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )
        filename = f"{self.filename}_{timestamp}_{random_hash}.json"
        return Path(self.persist_dir) / filename


class LogManager:
    """
    Thread-safe log manager supporting async operations and file persistence.
    Handles concurrent log updates, automatic capacity management, and file I/O.

    Features:
        - Async locking for thread-safe operations
        - Automatic log rotation based on capacity
        - Configurable file persistence and cleanup
        - Graceful shutdown handling
    """

    def __init__(
        self, params: LogParams | None = None, logs: list[Log] | None = None
    ):
        """
        Initialize log manager with optional configuration and initial logs.

        Args:
            params: Custom logging parameters, uses defaults if None
            logs: Initial log entries to manage, starts empty if None
        """
        self.params = params or LogParams()
        self.logs: Pile[Log] = Pile(items=logs or [], strict_type=False)
        if self.params.auto_save_on_exit:
            atexit.register(self._sync_save_at_exit)

    async def log(self, log_: Log) -> None:
        """
        Add new log entry with capacity management and thread safety.
        Auto-dumps logs if capacity limit reached before adding new entry.

        Args:
            log_: Log entry to add, converted to Log type if needed
        """
        if not isinstance(log_, Log):
            log_ = Log(log_)
        if (
            self.params.capacity is not None
            and len(self.logs) >= self.params.capacity
        ):
            await self.dump(clear=self.params.clear_after_dump)

        async with self.logs:  # Acquire async lock
            self.logs.update(log_)

    async def dump(
        self, clear: bool | None = None, persist_path: str | Path | None = None
    ) -> None:
        """
        Thread-safely dump logs to file system with configurable cleanup.
        Generates unique filename if path not specified.

        Args:
            clear: Override default clear behavior, uses param setting if None
            persist_path: Optional specific file path, auto-generates if None

        Raises:
            Exception: If file write fails, with error logging
        """
        async with self.logs:
            if not self.logs:
                logging.debug("No logs to dump")
                return

            fp = persist_path or self.params.generate_filename()
            data = [log.to_dict() for log in self.logs]

        # Writing to file outside the lock to minimize lock duration
        try:
            await asyncio.to_thread(
                fp.write_text,
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logging.info(f"Successfully dumped logs to {fp}")
            if clear if clear is not None else self.params.clear_after_dump:
                async with self.logs:
                    self.logs.clear()
        except Exception as e:
            logging.error(f"Failed to dump logs: {e}")
            raise

    def _sync_save_at_exit(self) -> None:
        """
        Synchronous handler for atexit log saving.
        Ensures logs are saved during program shutdown.
        """
        if self.logs:
            try:
                asyncio.run(self.dump(clear=self.params.clear_after_dump))
            except Exception as e:
                logging.error(f"Failed to save logs on exit: {e}")

    def has_logs(self) -> bool:
        """
        Check if manager currently contains any logs.
        Returns:
            bool: True if logs exist, False if empty
        """
        return bool(self.logs)


# File: lion/protocols/log.py

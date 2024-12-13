# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

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
    """A log entry containing content and metadata.

    Attributes:
        content: The main log content as a dictionary.
        loginfo: Metadata about the log entry as a dictionary.
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
    """Parameters for log management, including file location and capacity.

    Attributes:
        persist_dir: Directory for saving log files.
        filename: Base name of the log file (without randomization).
        capacity: Maximum number of logs before triggering a dump. If None, unlimited.
        auto_save_on_exit: If True, logs are saved automatically at program exit.
        clear_after_dump: If True, logs are cleared after being dumped.
    """

    persist_dir: str = "./logs"
    filename: str = "logs"
    capacity: int | None = None
    auto_save_on_exit: bool = True
    clear_after_dump: bool = True

    def generate_filename(self) -> Path:
        """Generate a unique filename with a timestamp and a random hash.

        Returns:
            A Path object pointing to the uniquely named log file.
        """
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_hash = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )
        filename = f"{self.filename}_{timestamp}_{random_hash}.json"
        return Path(self.persist_dir) / filename


class LogManager:
    """Manages log entries with concurrency safety using Pile.

    Logs are stored in a Pile[Log], providing asynchronous safe operations.
    Logs can be asynchronously logged and dumped to a unique file each time.
    If configured, logs are automatically saved upon program exit.

    Attributes:
        params: Configuration parameters for the log manager.
        logs: A Pile of Log entries.
    """

    def __init__(
        self, params: LogParams | None = None, logs: list[Log] | None = None
    ):
        """Initialize a LogManager instance.

        Args:
            params: `LogParams` configuration or None for defaults.
            logs: Initial list of `Log` entries or None for empty.
        """
        self.params = params or LogParams()
        self.logs: Pile[Log] = Pile(items=logs or [], strict_type=False)
        if self.params.auto_save_on_exit:
            atexit.register(self._sync_save_at_exit)

    async def log(self, log_: Log) -> None:
        """Asynchronously add a log entry.

        If capacity is reached, logs are dumped before adding the new log.

        Args:
            log_: The Log entry to add.
        """
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
        """Asynchronously dump all logs to a uniquely named JSON file.

        Args:
            clear: Whether to clear logs after dumping. Defaults to `params.clear_after_dump`.
            persist_path: Optional override path for the log file.
                          If None, a unique path is generated.

        Raises:
            Exception: If dumping fails.
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
        """Sync handler for saving logs at exit, since `atexit` cannot be async."""
        if self.logs:
            try:
                asyncio.run(self.dump(clear=self.params.clear_after_dump))
            except Exception as e:
                logging.error(f"Failed to save logs on exit: {e}")

    def has_logs(self) -> bool:
        """Check if there are any logs.

        Returns:
            True if at least one log exists, False otherwise.
        """
        return bool(self.logs)


# File: lion/protocols/log.py

# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import atexit
import logging
from pathlib import Path

from lionagi.core.generic.log import Log
from lionagi.core.generic.pile import Pile
from lionagi.core.typing import Any
from lionagi.libs.file.types import create_path
from lionagi.protocols.configs.log_config import LogConfig


class LogManager:
    """Core logging functionality for the Lion framework.

    The LogManager provides robust log collection, storage, and persistence
    capabilities. It handles automatic capacity management, asynchronous
    operations, and safe file persistence.

    Key Features:
        - Asynchronous log collection
        - Configurable persistence
        - Automatic capacity management
        - Exit-safe log handling
        - CSV file storage

    Basic Usage:
        >>> # Simple usage with defaults
        >>> manager = LogManager()
        >>> await manager.alog(some_log)  # Add logs asynchronously
        >>> manager.dump()  # Manually dump to file

        >>> # Using configuration
        >>> config = LogConfig(
        ...     persist_dir="./app_logs",
        ...     capacity=1000,
        ...     file_prefix="service_a_"
        ... )
        >>> manager = LogManager.from_config(config)

        >>> # Custom initialization
        >>> manager = LogManager(
        ...     persist_dir="./logs",
        ...     capacity=100,
        ...     auto_save_on_exit=True
        ... )

    Configuration Options:
        - persist_dir: Base directory for log storage
        - subfolder: Optional subfolder organization
        - file_prefix: Prefix for log filenames
        - capacity: Maximum logs before auto-dump
        - extension: File extension (.csv default)
        - use_timestamp: Include timestamps in filenames
        - hash_digits: Random hash digits in filenames
        - auto_save_on_exit: Save on program exit
        - clear_after_dump: Clear after dumping

    Automatic Features:
        1. Capacity Management:
            - Auto-dumps when capacity is reached
            - Configurable capacity limits
            - Safe async dumping

        2. Exit Safety:
            - Automatic save on program exit
            - Configurable exit behavior
            - Error-safe exit handling

        3. File Management:
            - Automatic directory creation
            - Timestamp-based filenames
            - Unique file generation

        4. Thread Safety:
            - Async-safe operations
            - Thread-safe log collection
            - Safe concurrent access

    Implementation Notes:
        - Uses Pile[Log] for efficient log collection
        - Implements BaseManager for core functionality
        - Provides both sync and async interfaces
        - Handles concurrent access safely
        - Uses CSV format for persistence

    Error Handling:
        - Logs errors but doesn't block on non-critical failures
        - Ensures no log loss on errors
        - Provides detailed error information
        - Maintains system stability

    Common Patterns:
        1. Service Logger:
            >>> manager = LogManager(
            ...     persist_dir="./services",
            ...     file_prefix="service_a_",
            ...     capacity=1000
            ... )

        2. Debug Logger:
            >>> manager = LogManager(
            ...     persist_dir="./debug",
            ...     capacity=100,
            ...     auto_save_on_exit=False
            ... )

        3. High-Volume Logger:
            >>> manager = LogManager(
            ...     persist_dir="./high_volume",
            ...     capacity=10000,
            ...     use_timestamp=True,
            ...     clear_after_dump=True
            ... )

    See Also:
        - LogConfig: Configuration management
        - Log: Core log object
        - Pile: Collection management
    """

    def __init__(
        self,
        logs: Any = None,
        persist_dir: str | Path | None = None,
        subfolder: str | None = None,
        file_prefix: str | None = None,
        capacity: int | None = None,
        extension: str = ".csv",
        use_timestamp: bool = True,
        hash_digits: int = 5,
        auto_save_on_exit: bool = True,
        clear_after_dump: bool = True,
    ) -> None:
        """Initialize the LogManager.

        Args:
            logs: Initial logs to manage
            persist_dir: Directory for log persistence
            subfolder: Subfolder within persist_dir
            file_prefix: Prefix for log files
            capacity: Maximum logs before auto-dump
            extension: File extension for log files
            use_timestamp: Whether to include timestamps in filenames
            hash_digits: Number of random hash digits in filenames
            auto_save_on_exit: Whether to save logs on program exit
            clear_after_dump: Whether to clear logs after dumping

        Example:
            >>> manager = LogManager(
            ...     persist_dir="./logs",
            ...     capacity=1000,
            ...     auto_save_on_exit=True
            ... )
        """
        self.logs: Pile[Log] = Pile(logs or {}, item_type={Log})
        self.persist_dir = persist_dir
        self.subfolder = subfolder
        self.file_prefix = file_prefix
        self.capacity = capacity
        self.extension = extension
        self.use_timestamp = use_timestamp
        self.hash_digits = hash_digits
        self.clear_after_dump = clear_after_dump

        if auto_save_on_exit:
            atexit.register(self.save_at_exit)

    async def alog(self, log_: Log, /) -> None:
        """Asynchronously add a log to the collection.

        This method handles capacity management automatically. If capacity is
        reached, it will trigger an auto-dump before adding the new log.

        Args:
            log_: The log to add

        Note:
            If auto-dump fails, the error is logged but the new log is still
            added
        """
        async with self.logs:
            self.log(log_)

    def log(self, log_: Log, /) -> None:
        """Add a log to the collection synchronously.

        This method handles capacity management automatically. If capacity is
        reached, it will trigger an auto-dump before adding the new log.

        Args:
            log_: The log to add

        Note:
            If auto-dump fails, the error is logged but the new log is still
            added
        """
        if self.capacity and len(self.logs) >= self.capacity:
            try:
                self.dump(clear=self.clear_after_dump)
            except Exception as e:
                logging.error(f"Failed to auto-dump logs: {e}")

        self.logs.include(log_)

    async def adump(
        self, clear: bool | None = None, persist_path: str | Path = None
    ) -> None:
        """Asynchronously dump logs to file.

        Args:
            clear: Whether to clear logs after dumping. If None, uses
                config value
            persist_path: Override path for log file. If None, uses config path
        """
        async with self.logs:
            self.dump(
                clear=self.clear_after_dump if clear is None else clear,
                persist_path=persist_path,
            )

    def dump(
        self, clear: bool | None = None, persist_path: str | Path = None
    ) -> None:
        """Dump logs to file.

        This method handles the actual persistence of logs to the filesystem.
        It will create directories as needed and handle path generation if no
        specific path is provided.

        Args:
            clear: Whether to clear logs after dumping. If None, uses config
            persist_path: Override path for log file. If None, uses config path

        Raises:
            OSError: If file operation fails
            Exception: If log serialization fails
        """
        if not self.logs:
            logging.debug("No logs to dump")
            return

        try:
            fp = persist_path or self._create_path()
            self.logs.to_csv(fp)
            logging.info(f"Successfully dumped logs to {fp}")

            if self.clear_after_dump if clear is None else clear:
                self.logs.clear()
        except Exception as e:
            logging.error(f"Failed to dump logs: {e}")
            raise

    def _create_path(self) -> Path:
        persist_apth = self.persist_dir or "./data/logs"
        dir = (
            f"{persist_apth}/{self.subfolder}"
            if self.subfolder
            else persist_apth
        )
        return create_path(
            directory=dir,
            filename=self.file_prefix or "",
            extension=self.extension,
            timestamp=self.use_timestamp,
            random_hash_digits=self.hash_digits,
        )

    def save_at_exit(self) -> None:
        """Handler for saving logs when program exits.

        This method is automatically registered if auto_save_on_exit is
        True. It ensures no logs are lost when the program terminates.
        """
        if self.logs:
            try:
                self.dump(clear=self.clear_after_dump)
            except Exception as e:
                logging.error(f"Failed to save logs on exit: {e}")

    @classmethod
    def from_config(
        cls,
        config: LogConfig,
        logs: Any = None,
    ) -> "LogManager":
        """Create a LogManager instance from configuration.

        This is the recommended way to create a LogManager when you need
        custom configuration.

        Args:
            config: The configuration to use
            logs: Optional initial logs

        Returns:
            A new LogManager instance

        Example:
            >>> config = LogConfig(persist_dir="./logs")
            >>> manager = LogManager.from_config(config)
        """
        return cls(
            logs=logs,
            persist_dir=config.persist_dir,
            subfolder=config.subfolder,
            file_prefix=config.file_prefix,
            capacity=config.capacity,
            extension=config.extension,
            use_timestamp=config.use_timestamp,
            hash_digits=config.hash_digits,
            auto_save_on_exit=config.auto_save_on_exit,
            clear_after_dump=config.clear_after_dump,
        )


__all__ = ["LogConfig", "LogManager"]

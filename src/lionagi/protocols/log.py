# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import atexit
import logging
from pathlib import Path
from typing import Any, Self

from pydantic import Field, PrivateAttr, field_serializer, field_validator

from lionagi.libs.parse.types import to_dict
from lionagi.utils import create_path

from .base import AccessError, Manager
from .element import Element
from .log import Log
from .models import Note, SchemaModel
from .pile import Pile

__all__ = (
    "Log",
    "LogConfig",
    "LogManager",
)


class Log(Element):
    content: Note = Field(
        default_factory=Note,
        title="Log Content",
        description="The content of the log entry.",
    )

    loginfo: Note = Field(
        default_factory=Note,
        title="Log Info",
        description="Metadata about the log entry.",
    )

    _immutable: bool = PrivateAttr(False)

    def __init__(self, content: Note, loginfo: Note, **kwargs) -> None:
        super().__init__(**kwargs)
        self.content = self._validate_note(content)
        self.loginfo = self._validate_note(loginfo)

    @classmethod
    def _validate_load_data(cls, data: dict, /) -> dict:
        try:
            data["id"] = data.pop("log_id")
            data["timestamp"] = data.pop("log_timestamp")
            data["lion_class"] = data.pop("log_class")
            return data
        except Exception as e:
            raise AccessError(
                "Log can only be loaded from a previously saved log entries.",
            ) from e

    @classmethod
    def from_dict(cls, data: dict, /) -> Self:
        data = cls._validate_load_data(data)
        self = cls(**data)
        self._immutable = True
        return self

    def __setattr__(self, name: str, value: Any, /) -> None:
        if self._immutable:
            raise AttributeError("Cannot modify immutable log entry.")
        super().__setattr__(name, value)

    def _validate_note(cls, value: Any, /) -> Note:
        if not value:
            return Note()
        if isinstance(value, Note):
            return value
        if isinstance(value, dict):
            return Note(**value)
        try:
            return Note(**to_dict(value))
        except Exception as e:
            raise e

    @field_serializer("content", "loginfo")
    def _serialize_note(self, value: Note) -> dict:
        return value.to_dict()

    def to_dict(self) -> dict:
        dict_ = super().to_dict()
        dict_["log_id"] = dict_.pop("id")
        dict_["log_class"] = dict_.pop("lion_class")
        dict_["log_timestamp"] = dict_.pop("timestamp")
        dict_ = to_dict(
            dict_,
            recursive=True,
            recursive_python_only=False,
            max_recursive_depth=5,
        )
        return dict_


class LogConfig(SchemaModel):
    """Configuration for log management.

    This class defines all configuration options for LogManager behavior
    including file paths, persistence strategies, and capacity management.

    Attributes:
        persist_dir: Base directory for log storage
        subfolder: Optional subfolder within persist_dir
        file_prefix: Prefix for log filenames
        capacity: Maximum logs before auto-dump
        extension: File extension for log files
        use_timestamp: Whether to include timestamps in filenames
        hash_digits: Random hash digits in filenames
        auto_save_on_exit: Whether to save on program exit
        clear_after_dump: Whether to clear after dumping
    """

    # Basic settings
    persist_dir: Path | str | None = Field(
        default="./data/logs", description="Base directory for log persistence"
    )
    subfolder: str | None = Field(
        default=None,
        description="Optional subfolder within persist_dir",
    )
    file_prefix: str | None = Field(
        default=None, description="Prefix for log filenames"
    )
    capacity: int | None = Field(
        default=None,
        description="Maximum number of logs to keep in memory before dumping",
    )

    # File configuration
    extension: str = Field(
        default=".csv",
        description="File extension for log files",
        pattern=r"^\.[a-zA-Z0-9]+$",
    )
    use_timestamp: bool = Field(
        default=True, description="Whether to include timestamp in filenames"
    )
    hash_digits: int = Field(
        default=5,
        description="Number of random hash digits to add to filenames",
        ge=0,
        le=10,
    )

    # Behavior settings
    auto_save_on_exit: bool = Field(
        default=True,
        description="Whether to automatically save logs when program exits",
    )
    clear_after_dump: bool = Field(
        default=True, description="Whether to clear logs after dumping to file"
    )

    @field_validator("persist_dir")
    def validate_persist_dir(cls, v: Any) -> Path:
        """Validate and convert persist_dir to Path."""
        if v is None:
            return Path("./data/logs")
        return Path(v)

    @field_validator("capacity")
    def validate_capacity(cls, v: Any) -> int | None:
        """Validate capacity is positive if set."""
        if v is not None and v <= 0:
            raise ValueError("Capacity must be positive")
        return v


class LogManager(Manager):

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


        """
        # Initialize log collection
        self.logs: Pile[Log] = Pile(logs or {}, item_type={Log})

        # Store configuration
        self.persist_dir = persist_dir
        self.subfolder = subfolder
        self.file_prefix = file_prefix
        self.capacity = capacity
        self.extension = extension
        self.use_timestamp = use_timestamp
        self.hash_digits = hash_digits
        self.clear_after_dump = clear_after_dump

        # Register exit handler if configured
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

        # Check capacity before adding
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
        """Create a path for log file based on configuration.

        Returns:
            Path: The constructed file path

        Note:
            Uses the lion.funcs.create_path utility for path generation
        """
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


# File: lion/protocols/log.py

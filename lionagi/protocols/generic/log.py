from __future__ import annotations

import atexit
import logging
from pathlib import Path
from typing import Any, ClassVar

from pydantic import Field, field_serializer, field_validator

from lionagi.utils import Params, ToDictParams, create_path

from .element import Element
from .pile import Pile

_to_dict: ToDictParams = ToDictParams(
    use_model_dump=True,
    recursive=True,
    max_recursive_depth=5,
    recursive_python_only=False,
    use_enum_values=True,
)

__all__ = (
    "LogManagerConfig",
    "Log",
    "LogManager",
)


class LogManagerConfig(Params):
    """Configuration for log management.

    Attributes:
        persist_dir: Directory for log storage
        subfolder: Optional subdirectory within persist_dir
        file_prefix: Prefix for log filenames
        capacity: Maximum logs before auto-dump
        extension: File extension for logs
        use_timestamp: Include timestamp in filenames
        hash_digits: Length of random hash in filenames
        auto_save_on_exit: Save logs on program exit
        clear_after_dump: Clear logs after saving
    """

    persist_dir: str | Path = "./data/logs"
    subfolder: str | None = None
    file_prefix: str | None = None
    capacity: int | None = None
    extension: str = ".csv"
    use_timestamp: bool = True
    hash_digits: int = 5
    auto_save_on_exit: bool = True
    clear_after_dump: bool = True

    @field_validator("extension", mode="before")
    def ensure_extension_has_dot(cls, v):
        """Ensure file extension starts with dot."""
        if not v.startswith("."):
            return "." + v
        return v


class Log(Element):
    """Immutable log entry containing arbitrary element data.

    Attributes:
        content: Element to be logged
        immutable: Whether log can be modified
    """

    serialized_keys: ClassVar[set[str]] = {
        "content",
        "log_id",
        "log_created_at",
        "log_class",
        "immutable",
    }
    content: Element
    immutable: bool = Field(default=False, frozen=True)

    @field_serializer("content")
    def _serialize_content(self, content: Element) -> dict:
        return content.to_dict()

    @field_validator("content", mode="before")
    def _validate_content(cls, value: dict) -> Element:
        return Element.from_dict(value)

    def to_dict(self) -> dict:
        """Convert log to dictionary with standardized keys."""
        dict_ = super().to_dict()
        dict_["log_class"] = dict_.pop("lion_class")
        dict_["log_id"] = dict_.pop("id")
        dict_["log_created_at"] = dict_.pop("created_at")
        return _to_dict(dict_)

    @classmethod
    def from_dict(cls, data: dict) -> Log:
        """Create log from dictionary with required keys."""
        if set(data.keys()) == cls.serialized_keys:
            return Log(
                content=data["content"],
                id=data["log_id"],
                created_at=data["log_created_at"],
                immutable=data["immutable"],
            )
        raise ValueError("Invalid Log data, must come from Log.to_dict()")

    def __setattr__(self, name, value):
        if self.immutable:
            raise AttributeError("immutable attribute is read-only")
        return super().__setattr__(name, value)

    @classmethod
    def create(cls, content: Element, /) -> Log:
        """Create new log entry from element."""
        return cls(content=content)


class LogManager:
    """Manages collection and persistence of logs.

    Handles automatic log rotation, file persistence, and clean-up based on
    configured capacity and file path settings.
    """

    def __init__(
        self,
        logs: Pile[Log] = None,
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
        if isinstance(logs, Pile):
            logs = list(logs)
        self.logs: Pile[Log] = Pile(collections=(logs or {}), item_type={Log})
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
        """Add log asynchronously, handling capacity limits."""
        async with self.logs:
            self.log(log_)

    def log(self, log_: Log, /) -> None:
        """Add log synchronously, handling capacity limits."""
        if self.capacity and len(self.logs) >= self.capacity:
            try:
                self.dump(clear=self.clear_after_dump)
            except Exception as e:
                logging.error(f"Failed to auto-dump logs: {e}")

        self.logs.include(log_)

    async def adump(
        self, clear: bool | None = None, persist_path: str | Path = None
    ) -> None:
        """Dump logs asynchronously to file."""
        async with self.logs:
            self.dump(
                clear=self.clear_after_dump if clear is None else clear,
                persist_path=persist_path,
            )

    def dump(
        self, clear: bool | None = None, persist_path: str | Path = None
    ) -> None:
        """Dump logs to file, with optional clearing."""
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
        """Generate file path based on configuration."""
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
        """Save remaining logs when program exits."""
        if self.logs:
            try:
                self.dump(clear=self.clear_after_dump)
            except Exception as e:
                logging.error(f"Failed to save logs on exit: {e}")

    @classmethod
    def from_config(
        cls, config: LogManagerConfig, logs: Any = None
    ) -> LogManager:
        """Create manager from configuration object."""
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

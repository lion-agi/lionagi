# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import atexit
import logging
from pathlib import Path
from typing import Any

from pydantic import PrivateAttr

from lionagi.utils import create_path, to_dict

from .._concepts import Manager
from .element import Element
from .pile import Pile

__all__ = (
    "LogManagerConfig",
    "Log",
    "LogManager",
)


class LogManagerConfig:
    """
    Configuration for log management, controlling output paths,
    file naming patterns, and capacity limits.
    """

    def __init__(
        self,
        persist_dir: str | Path = "./data/logs",
        subfolder: str | None = None,
        file_prefix: str | None = None,
        capacity: int | None = None,
        extension: str = ".json",
        use_timestamp: bool = True,
        hash_digits: int = 5,
        auto_save_on_exit: bool = True,
        clear_after_dump: bool = True,
    ):
        # Ensure extension starts with a dot
        if not extension.startswith("."):
            extension = "." + extension

        self.persist_dir = persist_dir
        self.subfolder = subfolder
        self.file_prefix = file_prefix
        self.capacity = capacity
        self.extension = extension
        self.use_timestamp = use_timestamp
        self.hash_digits = hash_digits
        self.auto_save_on_exit = auto_save_on_exit
        self.clear_after_dump = clear_after_dump


class Log(Element):
    """
    An immutable log entry that wraps a dictionary of content.

    Once created or restored from a dictionary, the log is marked
    as read-only.
    """

    content: dict[str, Any]
    _immutable: bool = PrivateAttr(False)

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutation if log is immutable."""
        if getattr(self, "_immutable", False):
            raise AttributeError("This Log is immutable.")
        super().__setattr__(name, value)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Log:
        """
        Create a Log from a dictionary previously produced by `to_dict`.

        The dictionary must contain keys in `serialized_keys`.
        """
        self = cls.model_validate(data)
        self._immutable = True
        return self

    @classmethod
    def create(cls, content: Element) -> Log:
        """
        Create a new Log from an Element, storing a dict snapshot
        of the element's data.
        """
        return cls(
            content=to_dict(
                content,
                recursive=True,
                recursive_python_only=False,
                suppress=True,
                max_recursive_depth=5,
            )
        )


class LogManager(Manager):
    """
    Manages a collection of logs, optionally auto-dumping them
    to CSV or JSON when capacity is reached or at program exit.
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
    ):
        """
        Args:
            logs: Initial logs (list or Pile of Log objects).
            persist_dir: Directory for log files (default "./data/logs").
            subfolder: Subdirectory within `persist_dir`.
            file_prefix: Filename prefix for log files.
            capacity: Max number of logs before auto-dump. None = unlimited.
            extension: File extension (".csv" or ".json").
            use_timestamp: Whether to include timestamps in filenames.
            hash_digits: Random hash length in filenames.
            auto_save_on_exit: Auto-save logs at program exit.
            clear_after_dump: Whether to clear logs after saving.
        """
        super().__init__()
        if logs is None:
            logs = []
        # Convert logs to a list if it's already a Pile
        if isinstance(logs, Pile):
            logs = logs.to_list()

        self.logs: Pile[Log] = Pile(
            collections=logs, item_type=Log, strict_type=True
        )

        # Store config
        self.persist_dir = persist_dir or "./data/logs"
        self.subfolder = subfolder
        self.file_prefix = file_prefix
        self.capacity = capacity
        self.extension = extension
        self.use_timestamp = use_timestamp
        self.hash_digits = hash_digits
        self.clear_after_dump = clear_after_dump

        # Auto-dump on exit
        if auto_save_on_exit:
            atexit.register(self.save_at_exit)

    def log(self, log_: Log) -> None:
        """
        Add a log synchronously. If capacity is reached, auto-dump to file.
        """
        if self.capacity and len(self.logs) >= self.capacity:
            try:
                self.dump(clear=self.clear_after_dump)
            except Exception as e:
                logging.error(f"Failed to auto-dump logs: {e}")
        self.logs.append(log_)

    async def alog(self, log_: Log) -> None:
        """
        Add a log asynchronously. If capacity is reached, auto-dump to file.
        """
        async with self.logs:
            self.log(log_)

    def dump(
        self,
        clear: bool | None = None,
        persist_path: str | Path | None = None,
    ) -> None:
        """
        Dump the logs to a file (CSV or JSON). If file extension is
        unsupported, raise ValueError. Optionally clear logs after.
        """
        if not self.logs:
            logging.debug("No logs to dump.")
            return

        fp = persist_path or self._create_path()
        suffix = fp.suffix.lower()
        try:
            if suffix == ".csv":
                self.logs.to_csv_file(fp)
            elif suffix == ".json":
                self.logs.to_json_file(fp)
            else:
                raise ValueError(f"Unsupported file extension: {suffix}")

            logging.info(f"Dumped logs to {fp}")
            do_clear = self.clear_after_dump if clear is None else clear
            if do_clear:
                self.logs.clear()
        except Exception as e:
            logging.error(f"Failed to dump logs: {e}")
            raise

    async def adump(
        self,
        clear: bool | None = None,
        persist_path: str | Path | None = None,
    ) -> None:
        """Asynchronously dump the logs to a file."""
        async with self.logs:
            self.dump(clear=clear, persist_path=persist_path)

    def _create_path(self) -> Path:
        """
        Build a file path from the manager's config using
        `create_path`.
        """
        path_str = str(self.persist_dir)
        if self.subfolder:
            path_str = f"{path_str}/{self.subfolder}"
        return create_path(
            directory=path_str,
            filename=self.file_prefix or "",
            extension=self.extension,
            timestamp=self.use_timestamp,
            random_hash_digits=self.hash_digits,
        )

    def save_at_exit(self) -> None:
        """Dump logs on program exit."""
        if self.logs:
            try:
                self.dump(clear=self.clear_after_dump)
            except Exception as e:
                logging.error(f"Failed to save logs on exit: {e}")

    @classmethod
    def from_config(
        cls, config: LogManagerConfig, logs: Any = None
    ) -> LogManager:
        """
        Construct a LogManager from a LogManagerConfig.
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


# File: lionagi/protocols/generic/log.py

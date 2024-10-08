import atexit
import json
import os
from pathlib import Path
from typing import Any, TypeVar

from lionabc import BaseManager

from lion_core.generic.log import Log
from lion_core.generic.pile import Pile, pile

T = TypeVar("T", bound=Log)


class LogManager(BaseManager):
    """Manages logging operations and persistence."""

    def __init__(
        self,
        logs: Any = None,
        persist_dir: str | None = None,
        persist_path: str | None = None,
        subfolder: str | None = None,
        file_prefix: str | None = None,
    ) -> None:
        """Initialize the LogManager.

        Args:
            logs: Initial logs to manage.
            persist_dir: Directory for log persistence.
            persist_path: Full path for log persistence.
            subfolder: Subfolder within persist_dir.
            file_prefix: Prefix for log files.
        """
        self.logs: Pile[T] = pile(logs or {}, item_type={Log})
        self.persist_dir = persist_dir
        self.persist_path = persist_path
        self.file_prefix = file_prefix
        self.subfolder = subfolder
        atexit.register(self.save_at_exit)

    async def alog(self, log_: Log, /) -> None:
        """Asynchronously add a log to the pile.

        Args:
            log_: The log to add.
        """
        await self.logs.ainclude(log_)

    async def adump(
        self, clear: bool = True, persist_path: str | Path | None = None
    ) -> dict:
        """Asynchronously dump logs and save them.

        Args:
            clear: Whether to clear logs after dumping.
            persist_path: Path to save the dumped logs.

        Returns:
            The dumped log data.
        """
        async with self.logs.async_lock:
            id_ = self.logs[-1].ln_id[:-6]
            data = self.logs.to_dict()
            if clear:
                self.logs.clear()
            self._save(id_=id_, data=data, persist_path=persist_path)
        return data

    def dump(
        self, clear: bool = True, persist_path: str | Path | None = None
    ) -> dict:
        """Dump logs and save them.

        Args:
            clear: Whether to clear logs after dumping.
            persist_path: Path to save the dumped logs.

        Returns:
            The dumped log data.
        """
        id_ = self.logs[-1].ln_id[:-6]
        data = self.logs.to_dict()
        if clear:
            self.logs.clear()
        self._save(id_=id_, data=data, persist_path=persist_path)
        return data

    def _save(
        self, id_: str, data: dict, persist_path: str | Path | None = None
    ) -> None:
        """Save log data to a file.

        Args:
            id_: Identifier for the log file.
            data: Log data to save.
            persist_path: Path to save the log file.
        """
        persist_path = persist_path or self.persist_path

        if not persist_path:
            persist_dir = self.persist_dir or "./data/logs"
            if str(persist_dir).endswith("/"):
                persist_dir = str(persist_dir)[:-1]
            if self.subfolder:
                persist_dir = f"{persist_dir}/{self.subfolder}"
            persist_path = f"{persist_dir}/{self.file_prefix or ''}{id_}.json"

        os.makedirs(os.path.dirname(persist_path), exist_ok=True)

        with open(persist_path, "w") as f:
            json.dump(data, f)

    def load_json(self, persist_path: str | Path | None = None) -> None:
        """Load logs from a JSON file.

        Args:
            persist_path: Path to load the log file from.

        Raises:
            FileNotFoundError: If the log file is not found.
        """
        persist_path = persist_path or self.persist_path
        try:
            with open(persist_path) as f:
                data = json.load(f)
            self.logs = Pile.load(data=data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Log file not found at {persist_path}")

    def save_at_exit(self) -> None:
        """Save logs when exiting the program."""
        if self.logs:
            self.dump(clear=True)


# File: lion_core/log/log_manager.py

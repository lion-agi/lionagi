.. _lionagi_protocols_generic_log:

===========================================================
Log, LogManager, and Config
===========================================================
.. module:: lionagi.protocols.generic.log
   :synopsis: Provides a log manager system for storing and persisting logs.

Overview
--------
This module introduces:

- A :class:`LogManagerConfig` class that holds configuration for where and how
  logs are stored (directory, file naming, capacity, etc.).
- A :class:`Log` class, an **immutable** record wrapping a dictionary of data.
- A :class:`LogManager` class, which manages collections of :class:`Log` objects,
  handles persistence (CSV/JSON), and enforces capacity-based auto-saving.

Contents
--------
.. contents::
   :local:
   :depth: 2


LogManagerConfig
----------------
.. class:: LogManagerConfig
   :module: lionagi.protocols.generic.log

   A **pydantic-based** configuration model that defines where logs should be stored, 
   how files are named, and whether auto-saving or clearing is performed on certain 
   conditions.

   Attributes
   ----------
   persist_dir : str | Path
       Base directory to store log files (defaults to ``"./data/logs"``).
   subfolder : str | None
       Optional subdirectory name inside :attr:`persist_dir`.
   file_prefix : str | None
       An optional prefix for log filenames.
   capacity : int | None
       Maximum number of logs before an auto-dump is triggered (None for no limit).
   extension : str
       File extension, must be one of ``.csv``, ``.json``, or ``.jsonl``.
   use_timestamp : bool
       If True, timestamps are included in file names.
   hash_digits : int | None
       Number of random hash digits to include in filenames (None for none).
   auto_save_on_exit : bool
       If True, logs are saved automatically when the Python process exits.
   clear_after_dump : bool
       If True, logs are cleared from memory after dumping to file.

   Validation
   ----------
   .. method:: _validate_non_negative(value) -> int
      :classmethod:

      Private class method that ensures that ``capacity`` and ``hash_digits`` are non-negative integers.

   .. method:: _ensure_dot_extension(value) -> str
      :classmethod:

      Private class method that ensures the extension starts with a dot and is one of the supported formats.

   Example
   -------
   .. code-block:: python

       from lionagi.protocols.generic.log import LogManagerConfig

       config = LogManagerConfig(
           persist_dir="logs",
           file_prefix="session",
           capacity=100,
           extension=".csv",
       )
       print(config)  # => LogManagerConfig(persist_dir='logs', ...)


Log
---
.. class:: Log(Element)
   :module: lionagi.protocols.generic.log

   **Inherits from**: :class:`~lionagi.protocols.generic.element.Element`

   Represents an **immutable** log entry, wrapping a dictionary of content. Once 
   created or loaded from a dictionary, its data can no longer be modified. This 
   ensures that all logs are preserved in their original state.

   Attributes
   ----------
   content : dict[str, Any]
       The primary content of the log entry, typically an arbitrary dictionary
       of metadata or snapshot data.

   Private Attributes
   ------------------
   .. attribute:: _immutable : bool

      Private flag indicating whether this log entry is locked from further changes.

   Methods
   -------
   .. method:: __setattr__(name: str, value: Any) -> None

      Prevents mutation if this log is already marked immutable. Raises
      :exc:`AttributeError` if a change is attempted.

   .. classmethod:: from_dict(data: dict[str, Any]) -> Log

      Creates a :class:`Log` from a dictionary. Marks the new log as immutable.

   .. classmethod:: create(cls, content: Element | dict) -> Log

      Constructs a new log from either an :class:`~lionagi.protocols.generic.element.Element`
      (using its :meth:`to_dict` method) or a dictionary. If the resulting content 
      is empty, a log entry with an error message is created.

   Example
   -------
   .. code-block:: python

       from lionagi.protocols.generic.log import Log
       from lionagi.protocols.generic.element import Element

       class UserSession(Element):
           def __init__(self, session_data):
               super().__init__()
               self.session_data = session_data

       session = UserSession({"user": "alice", "action": "login"})
       log_entry = Log.create(session)
       print(log_entry.content)


LogManager
----------
.. class:: LogManager(Manager)
   :module: lionagi.protocols.generic.log

   **Inherits from**: :class:`~lionagi.protocols._concepts.Manager`

   A manager that stores :class:`Log` objects in a :class:`~lionagi.protocols.generic.pile.Pile`.
   It optionally dumps them to files (CSV/JSON) automatically when certain conditions 
   are met (like reaching a capacity limit or application exit).

   Attributes
   ----------
   logs : Pile[Log]
       The collection of logs being managed.
   _config : LogManagerConfig
       Configuration parameters that control directory, file naming, 
       capacity, and auto-save behavior.

   Initialization
   --------------
   .. method:: __init__(*, logs: Any = None, _config: LogManagerConfig = None, **kwargs) -> None

      Initializes a LogManager. If ``_config`` is not provided, a new 
      :class:`LogManagerConfig` is created from additional keyword arguments.

      Parameters
      ----------
      logs : Any
          Initial logs, can be a dictionary, list, or existing :class:`Pile`.
      _config : LogManagerConfig | None
          If None, builds config from remaining kwargs.
      **kwargs
          Additional arguments passed to :class:`LogManagerConfig`.

      Notes
      -----
      If :attr:`auto_save_on_exit` is True, a dump is automatically performed 
      on interpreter shutdown.

   Methods
   -------
   .. method:: log(log_: Log) -> None

      Adds a log synchronously. If the capacity is reached, triggers a 
      :meth:`dump` call automatically.

   .. method:: alog(log_: Log) -> None
      :async:

      Asynchronous version of :meth:`log`, also checks capacity for auto-dump.

   .. method:: dump(clear: bool | None = None, persist_path: str | Path | None = None) -> None

      Dumps the logs to a file. If the extension is unsupported, raises a ``ValueError``.
      Can optionally clear logs from memory afterward.

   .. method:: adump(clear: bool | None = None, persist_path: str | Path | None = None) -> None
      :async:

      Async version of :meth:`dump`.

   .. method:: save_at_exit() -> None

      Called at interpreter exit if :attr:`LogManagerConfig.auto_save_on_exit` is True.
      Attempts to dump logs before shutdown.

   .. classmethod:: from_config(config: LogManagerConfig, logs: Any = None) -> LogManager

      Creates a new ``LogManager`` from a given config object, optionally 
      seeded with logs.

   Example
   -------
   .. code-block:: python

       from lionagi.protocols.generic.log import Log, LogManager, LogManagerConfig

       config = LogManagerConfig(capacity=10, extension=".json")
       manager = LogManager.from_config(config)

       # Create logs
       log_entry = Log.create({"event": "user_signup", "user": "bob"})
       manager.log(log_entry)   # add log synchronously

       # Dump logs manually
       manager.dump()


File Location
-------------
**Source File**: 
``lionagi/protocols/generic/log.py``

``Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>``
``SPDX-License-Identifier: Apache-2.0``

# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.core.generic.types import Element, Log
from lionagi.core.typing import Any, Enum, NoReturn, PrivateAttr, override
from lionagi.settings import Settings, TimedFuncCallConfig


class EventStatus(str, Enum):
    """Status states for tracking action execution progress.

    Attributes:
        PENDING: Initial state before execution starts
        PROCESSING: Action is currently being executed
        COMPLETED: Action completed successfully
        FAILED: Action failed during execution
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ObservableAction(Element):
    """Base class for actions that can be monitored and tracked.

    Provides functionality for tracking execution status, timing, and results
    of action invocations. Inherits from Element for serialization capabilities.

    Attributes:
        status (EventStatus): Current execution status of the action
        execution_time (float | None): Time taken to execute the action in seconds
        execution_response (Any): Result returned from the action execution
        execution_error (str | None): Error message if execution failed
        _timed_config (TimedFuncCallConfig): Configuration for timed execution
        _content_fields (list): Fields to include in content section of logs
    """

    status: EventStatus = EventStatus.PENDING
    execution_time: float | None = None
    execution_response: Any = None
    execution_error: str | None = None
    _timed_config: TimedFuncCallConfig | None = PrivateAttr(None)
    _content_fields: list = PrivateAttr(["execution_response"])

    @override
    def __init__(
        self, timed_config: dict | TimedFuncCallConfig | None, **kwargs: Any
    ) -> None:
        """Initialize an ObservableAction instance.

        Args:
            timed_config: Configuration for timed function execution.
                If None, uses default config from Settings.
                If dict, converts to TimedFuncCallConfig.
            **kwargs: Additional keyword arguments passed to TimedFuncCallConfig
                if timed_config is a dict.
        """
        super().__init__()
        if timed_config is None:
            self._timed_config = Settings.Config.TIMED_CALL

        else:
            if isinstance(timed_config, TimedFuncCallConfig):
                timed_config = timed_config.to_dict()
            if isinstance(timed_config, dict):
                timed_config = {**timed_config, **kwargs}
            timed_config = TimedFuncCallConfig(**timed_config)
            self._timed_config = timed_config

    def to_log(self) -> Log:
        """Convert the action to a log entry.

        Creates a structured log entry with execution details split into
        content and loginfo sections. Content includes execution results,
        while loginfo includes metadata and status information.

        Returns:
            Log: A log entry representing the action's execution state
                and results.
        """
        dict_ = self.to_dict()
        dict_["status"] = self.status.value
        content = {k: dict_[k] for k in self._content_fields if k in dict_}
        loginfo = {k: dict_[k] for k in dict_ if k not in self._content_fields}
        return Log(content=content, loginfo=loginfo)

    @classmethod
    def from_dict(cls, data: dict, /, **kwargs: Any) -> NoReturn:
        """Event cannot be re-created from dictionary.

        This method is intentionally not implemented as actions represent
        one-time events that should not be recreated from serialized state.

        Args:
            data: Dictionary of serialized action data
            **kwargs: Additional keyword arguments

        Raises:
            NotImplementedError: Always raised as actions cannot be recreated
        """
        raise NotImplementedError(
            "An event cannot be recreated. Once it's done, it's done."
        )


__all__ = ["ObservableAction"]

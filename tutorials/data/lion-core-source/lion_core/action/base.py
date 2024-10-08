from typing import Any, NoReturn

from lionabc import Action, EventStatus
from lionabc.exceptions import LionAccessError
from pydantic import PrivateAttr
from typing_extensions import override

from lion_core import event_log_manager
from lion_core.generic.element import Element
from lion_core.generic.log import Log
from lion_core.setting import (
    DEFAULT_TIMED_FUNC_CALL_CONFIG,
    TimedFuncCallConfig,
)


class ObservableAction(Element, Action):

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
        super().__init__()
        if timed_config is None:
            self._timed_config = DEFAULT_TIMED_FUNC_CALL_CONFIG

        else:
            if isinstance(timed_config, TimedFuncCallConfig):
                timed_config = timed_config.to_dict()
            if isinstance(timed_config, dict):
                timed_config = {**timed_config, **kwargs}
            timed_config = TimedFuncCallConfig(**timed_config)
            self._timed_config = timed_config

    async def alog(self) -> Log:
        """Log the action asynchronously."""
        await event_log_manager.alog(self.to_log())

    def to_log(self) -> Log:
        """
        Convert the action to a log entry.

        Returns:
            BaseLog: A log entry representing the action.
        """
        dict_ = self.to_dict()
        content = {k: dict_[k] for k in self._content_fields if k in dict_}
        loginfo = {k: dict_[k] for k in dict_ if k not in self._content_fields}
        return Log(content=content, loginfo=loginfo)

    @classmethod
    def from_dict(cls, data: dict, /, **kwargs: Any) -> NoReturn:
        """Event cannot be re-created."""
        raise LionAccessError(
            "An event cannot be recreated. Once it's done, it's done."
        )


__all__ = ["ObservableAction"]
# File: lion_core/action/base.py

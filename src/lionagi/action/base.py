# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, NoReturn

from pydantic import PrivateAttr

from lionagi.protocols.types import (
    AccessError,
    Element,
    Event,
    EventStatus,
    Log,
)


class Action(Element, Event):

    status: EventStatus = EventStatus.PENDING
    execution_time: float | None = None
    execution_response: Any = None
    execution_error: str | None = None
    _content_fields: list = PrivateAttr(["execution_response"])

    def to_log(self) -> Log:
        """
        Convert the action to a log entry. Will forcefully convert all fields
        into a dictionary or json serializable format.

        Returns:
            BaseLog: A log entry representing the action.
        """
        dict_ = self.to_dict()
        dict_["status"] = self.status.value
        content = {k: dict_[k] for k in self._content_fields if k in dict_}
        loginfo = {k: dict_[k] for k in dict_ if k not in self._content_fields}
        return Log(content=content, loginfo=loginfo)

    @classmethod
    def from_dict(cls, data: dict, /, **kwargs: Any) -> NoReturn:
        """Event cannot be re-created."""
        raise AccessError(
            "An event cannot be recreated. Once it's done, it's done."
        )


__all__ = ["ObservableAction"]
# File: lion_core/action/base.py

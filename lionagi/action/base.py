# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, NoReturn

from pydantic import field_serializer

from ..protocols.base import Event, EventStatus
from ..protocols.log import Log
from ..protocols.models import BaseAutoModel

__all__ = ("Action",)


class Action(BaseAutoModel, Event):

    status: EventStatus = EventStatus.PENDING
    execution_time: float | None = None
    execution_result: Any | None = None
    error: str | None = None

    @field_serializer("status")
    def _serialize_status(self, value: EventStatus) -> str:
        return value.value

    def from_dict(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError(
            "An Action cannot be re-created from a dictionary."
        )

    def to_log(self) -> Log:
        return Log(content=self.to_dict())

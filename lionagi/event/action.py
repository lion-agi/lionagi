# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any, NoReturn

from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import override

from lionagi.core.action.tool import Tool
from lionagi.core.generic.types import Element, Log
from lionagi.libs.parse import to_dict
from lionagi.utils import TCallParams

from .base import Event, EventStatus, ExecutionResult
from .prompts import arguments_field_description, function_field_description
from .utils import parse_action_request_model


class ActionRequestModel(BaseModel):
    """
    Model for validating and processing action requests.

    Attributes:
        function: Name of function to execute
        arguments: Dictionary of function arguments
    """

    function: str | None = Field(None, description=function_field_description)
    arguments: dict | None = Field(
        default_factory=dict, description=arguments_field_description
    )

    @field_validator("arguments", mode="before")
    def _validate_arguments(cls, value: Any) -> dict[str, Any]:
        return to_dict(
            value,
            fuzzy_parse=True,
            suppress=True,
            recursive=True,
            recursive_python_only=False,
        )

    @classmethod
    def create(cls, content: str) -> list[BaseModel]:
        """Create request models from content string."""
        try:
            requests = parse_action_request_model(content)
            return (
                [cls.model_validate(req) for req in requests]
                if requests
                else []
            )
        except Exception:
            return []


class ActionResponseModel(BaseModel):
    """
    Model for capturing action execution results.

    Attributes:
        function: Name of executed function
        arguments: Arguments used in function call
        output: Function execution result

    Methods:
        create: Factory method to create response from request and output
    """

    function: str = Field(default_factory=str)
    arguments: dict[str, Any] = Field(default_factory=dict)
    execution_result: ExecutionResult = None

    @classmethod
    def create(
        cls,
        request: ActionRequestModel,
        output: Any,
        /,
    ) -> ActionResponseModel:
        return cls(
            function=request.function,
            arguments=request.arguments,
            output=output,
        )


class FunctionCalling(Element, Event):

    functool: Tool
    tcall: TCallParams
    request: ActionRequestModel
    status: EventStatus = EventStatus.PENDING
    execution_result: ExecutionResult | None = None

    @classmethod
    def create(
        cls,
        request: ActionRequestModel,
        functool: Tool,
        /,
        tcall: TCallParams = None,
        **kwargs,
    ) -> FunctionCalling:
        return cls(
            functool=functool,
            request=request,
            tcall=tcall
            or TCallParams(
                {k: v for k, v in kwargs.items() if k in TCallParams.keys()}
            ),
        )

    async def invoke(self) -> ExecutionResult: ...

    @property
    def response(self) -> ActionResponseModel: ...

    @model_validator(mode="before")
    def _validate_init(cls, data: dict):
        request = data.pop("request", None)
        if request is None or not isinstance(request, ActionRequestModel):
            raise ValueError(
                "Action request model is required, must be ActionRequestModel"
            )

        tcall = data.pop("tcall", TCallParams())

        ...

    @override
    def __init__(
        self, timed_config: dict | TimedFuncCallConfig | None, **kwargs: Any
    ) -> None:
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

    ...


class ObservableAction(Element):

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

# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from typing import Any

from pydantic import Field, model_validator

from lionagi.utils import RCallParams, is_coro_func

from ..generic.event import Event, EventStatus, Execution
from .tool import Tool


class FunctionCalling(Event):

    func_tool: Tool = Field(default=..., exclude=True)
    arguments: dict[str, Any] | None = None
    rcall_params: RCallParams | None = Field(default=None, exclude=True)

    @property
    def function(self):
        return self.func_tool.function

    @model_validator(mode="before")
    def _validate_rcall_params(cls, data: dict[str, Any]) -> dict[str, Any]:
        arguments: dict[str, Any] = data.get("arguments", {})
        if not isinstance(arguments, dict):
            raise ValueError("arguments must be a dictionary")

        func_tool = data.get("func_tool", None)
        if not isinstance(func_tool, Tool):
            raise ValueError("func_tool must be an instance of Tool")

        if func_tool.strict_func_call is True:
            if not set(arguments.keys()) == func_tool.required_fields:
                raise ValueError("arguments must match the function schema")
        else:
            if not func_tool.minimum_acceptable_fields.issubset(
                set(arguments.keys())
            ):
                raise ValueError("arguments must match the function schema")

        rcall_params = data.pop("rcall_params", None)
        if rcall_params is not None:
            if isinstance(rcall_params, dict):
                rcall_params = RCallParams(**rcall_params)
        else:
            rcall_params = RCallParams()

        return {
            "arguments": arguments,
            "func_tool": func_tool,
            "rcall_params": rcall_params,
        }

    async def invoke(self) -> Any:
        start = asyncio.get_event_loop().time()

        async def _inner(i):
            preprocessor = self.func_tool.preprocessor
            arguments = self.arguments

            if preprocessor is not None:
                if is_coro_func(preprocessor):
                    arguments = await preprocessor(
                        arguments, **self.func_tool.preprocessor_kwargs
                    )
                else:
                    arguments = preprocessor(
                        arguments, **self.func_tool.preprocessor_kwargs
                    )

            response = None
            if is_coro_func(self.func_tool.func_callable):
                response = await self.func_tool.func_callable(**arguments)
            else:
                response = self.func_tool.func_callable(**arguments)

            postprocessor = self.func_tool.postprocessor
            if postprocessor is not None:
                if is_coro_func(postprocessor):
                    response = await postprocessor(
                        response, **self.func_tool.postprocessor_kwargs
                    )
                else:
                    response = postprocessor(
                        response, **self.func_tool.postprocessor_kwargs
                    )
            return response

        try:
            response = await self.rcall_params(_inner)
            self.execution = Execution(
                status=EventStatus.COMPLETED,
                duration=asyncio.get_event_loop().time() - start,
                response=response,
            )
        except Exception as e:
            self.execution = Execution(
                status=EventStatus.FAILED,
                duration=asyncio.get_event_loop().time() - start,
                response=None,
                error=str(e),
            )

    def __str__(self) -> str:
        """Returns a string representation of the function call.

        Returns:
            A string in the format "function_name(arguments)".
        """
        return f"{self.func_tool.function}({self.arguments})"

    def __repr__(self) -> str:
        """Returns a detailed string representation of the function call.

        Returns:
            A string containing the class name and key attributes.
        """
        return (
            f"FunctionCalling(function={self.func_tool.function}, "
            f"arguments={self.arguments})"
        )

    def to_dict(self) -> dict:
        dict_ = super().to_dict()
        dict_["function"] = self.function
        dict_["arguments"] = self.arguments
        return dict_

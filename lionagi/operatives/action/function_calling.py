# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from typing import Any, Self

from pydantic import Field, model_validator

from lionagi.protocols.generic.event import Event, EventStatus
from lionagi.utils import is_coro_func

from .tool import Tool


class FunctionCalling(Event):
    """Handles asynchronous function execution with pre/post processing.

    This class manages function calls with optional preprocessing and
    postprocessing, handling both synchronous and asynchronous functions.
    """

    func_tool: Tool = Field(
        ...,
        description="Tool instance containing the function to be called",
        exclude=True,
    )

    arguments: dict[str, Any] = Field(
        ..., description="Dictionary of arguments to pass to the function"
    )

    @model_validator(mode="after")
    def _validate_strict_tool(self) -> Self:
        if self.func_tool.strict_func_call is True:
            if (
                not set(self.arguments.keys())
                == self.func_tool.required_fields
            ):
                raise ValueError("arguments must match the function schema")

        else:
            if not self.func_tool.minimum_acceptable_fields.issubset(
                set(self.arguments.keys())
            ):
                raise ValueError("arguments must match the function schema")
        return self

    @property
    def function(self):
        return self.func_tool.function

    async def invoke(self) -> None:
        """Execute the function call with pre/post processing.

        Handles both synchronous and asynchronous functions, including optional
        preprocessing of arguments and postprocessing of results.
        """
        start = asyncio.get_event_loop().time()

        async def _preprocess(kwargs):
            if is_coro_func(self.func_tool.preprocessor):
                return await self.func_tool.preprocessor(
                    kwargs, **self.func_tool.preprocessor_kwargs
                )
            return self.func_tool.preprocessor(
                kwargs, **self.func_tool.preprocessor_kwargs
            )

        async def _post_process(arg: Any):
            if is_coro_func(self.func_tool.postprocessor):
                return await self.func_tool.postprocessor(
                    arg, **self.func_tool.postprocessor_kwargs
                )
            return self.func_tool.postprocessor(
                arg, **self.func_tool.postprocessor_kwargs
            )

        async def _inner() -> Any:
            """Execute the function with pre/post processing.

            Returns:
                Function execution result after processing.
            """
            response = None
            if self.func_tool.preprocessor:
                self.arguments = await _preprocess(self.arguments)

            if is_coro_func(self.func_tool.func_callable):
                response = await self.func_tool.func_callable(**self.arguments)
            else:
                response = self.func_tool.func_callable(**self.arguments)

            if self.func_tool.postprocessor:
                response = await _post_process(response)
            return response

        try:
            response = await _inner()
            self.execution.duration = asyncio.get_event_loop().time() - start
            self.execution.status = EventStatus.COMPLETED
            self.execution.response = response
        except Exception as e:
            self.execution.duration = asyncio.get_event_loop().time() - start
            self.execution.status = EventStatus.FAILED
            self.execution.error = str(e)

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

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary.

        Returns:
            dict[str, Any]: Dictionary representation of the instance.
        """
        dict_ = super().to_dict()
        dict_["function"] = self.function
        dict_["arguments"] = self.arguments
        return dict_

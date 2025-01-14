# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Implements the `FunctionCalling` class, which extends the generic `Event`
model to handle a callable execution pipeline with optional pre/post
processing.
"""

import asyncio
from typing import Any, Self

from pydantic import Field, model_validator

from lionagi.protocols.generic.event import Event, EventStatus
from lionagi.utils import is_coro_func

from .tool import Tool


class FunctionCalling(Event):
    """
    An event that orchestrates function calls (synchronous or async)
    using a `Tool` object. Allows optional pre/post processing and
    records execution duration/status/results.
    """

    func_tool: Tool = Field(
        ...,
        description="A Tool instance containing the callable function definition.",
        exclude=True,
    )
    arguments: dict[str, Any] = Field(
        ...,
        description="Dictionary of arguments to pass to the function.",
    )
    
    @model_validator(mode="after")
    def _validate_strict_tool(self) -> Self:
        """
        Enforce required arguments if `strict_func_call` is True,
        or minimal required fields otherwise.
        """
        if self.func_tool.strict_func_call is True:
            # Must match exactly
            if not set(self.arguments.keys()) == self.func_tool.required_fields:
                raise ValueError("Arguments must match the function schema exactly.")
        else:
            # Must contain at least the minimal required fields
            if not self.func_tool.minimum_acceptable_fields.issubset(self.arguments):
                raise ValueError("Arguments must match the minimal function schema.")
        return self

    @property
    def function(self) -> str:
        """The name of the wrapped function (read from the tool schema)."""
        return self.func_tool.function

    async def invoke(self) -> None:
        """
        Execute the function call with optional pre/post processing.

        Execution flow:
          1) Preprocessor (if any) modifies `arguments`.
          2) The main callable is invoked (sync or async).
          3) Postprocessor (if any) modifies the result.
          4) Execution details are stored in `self.execution`.
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

        async def _postprocess(arg: Any):
            if is_coro_func(self.func_tool.postprocessor):
                return await self.func_tool.postprocessor(
                    arg, **self.func_tool.postprocessor_kwargs
                )
            return self.func_tool.postprocessor(
                arg, **self.func_tool.postprocessor_kwargs
            )

        async def _inner() -> Any:
            response = None
            if self.func_tool.preprocessor:
                self.arguments = await _preprocess(self.arguments)

            if is_coro_func(self.func_tool.func_callable):
                response = await self.func_tool.func_callable(**self.arguments)
            else:
                response = self.func_tool.func_callable(**self.arguments)

            if self.func_tool.postprocessor:
                response = await _postprocess(response)
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
        """String representation: function_name({arguments})."""
        return f"{self.func_tool.function}({self.arguments})"

    def __repr__(self) -> str:
        """Detailed representation with function and arguments."""
        return (
            f"FunctionCalling(function={self.func_tool.function}, arguments={self.arguments})"
        )

    def to_dict(self) -> dict[str, Any]:
        """Include function name and arguments in the serialized dict."""
        dict_ = super().to_dict()
        dict_["function"] = self.function
        dict_["arguments"] = self.arguments
        return dict_
    
# File: lionagi/operatives/action/function_calling.py
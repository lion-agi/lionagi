# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from typing import Any

from pydantic import Field, PrivateAttr
from typing_extensions import override

from lionagi.libs.func.params import TCallParams
from lionagi.utils import pre_post_process

from .action import Action, EventStatus
from .tool import Tool

__all__ = ("FunctionCalling",)


class FunctionCalling(Action):
    func_tool: Tool | None = Field(default=None, exclude=True)
    _content_fields: list = PrivateAttr(
        default=["execution_response", "arguments", "function"]
    )
    arguments: dict[str, Any] | None = None
    function: str | None = None
    tcall_params: TCallParams | None = None

    def __init__(
        self,
        func_tool: Tool,
        arguments: dict[str, Any],
        tcall_params: TCallParams = None,
        **kwargs: Any,
    ) -> None:
        """
        kwargs for timed config
        """
        super().__init__(**kwargs)
        self.func_tool = func_tool
        self.arguments = arguments or {}
        self.tcall_params = tcall_params or TCallParams()
        self.function = self.func_tool.function_name
        self.tcall_params.timing = True

    @override
    async def invoke(self) -> Any:
        """Asynchronously invokes the function with stored arguments.

        Handles function invocation, applying pre/post-processing steps.
        If a parser is defined, it's applied to the result before returning.

        Returns:
            Any: Result of the function call, possibly processed.

        Raises:
            Exception: If function call or processing steps fail.
        """

        @pre_post_process(
            preprocess=self.func_tool.pre_processor,
            preprocess_kwargs=self.func_tool.pre_processor_kwargs,
        )
        async def _inner(**kwargs) -> tuple[Any, Any | float]:
            kwargs["retry_timing"] = True
            result, elp = await self.tcall_params(
                self.func_tool.function, **kwargs
            )
            if self.func_tool.post_processor:
                _kwargs = self.func_tool.post_processor_kwargs or {}
                result, elp2 = await self.tcall_params(
                    self.func_tool.post_processor, result, **_kwargs
                )
                elp += elp2
            return result, elp

        start = asyncio.get_event_loop().time()
        try:
            result, elp = await _inner(**self.arguments)
            self.execution_response = result
            self.execution_time = elp
            self.status = EventStatus.COMPLETED

            if self.func_tool.parser is not None:
                if asyncio.iscoroutinefunction(self.func_tool.parser):
                    result = await self.func_tool.parser(result)
                else:
                    result = self.func_tool.parser(result)
            return result

        except Exception as e:
            self.status = EventStatus.FAILED
            self.execution_error = str(e)
            self.execution_time = asyncio.get_event_loop().time() - start

    def __str__(self) -> str:
        """Returns a string representation of the function call."""
        return f"{self.func_tool.function_name}({self.arguments})"

    def __repr__(self) -> str:
        """Returns a detailed string representation of the function call."""
        return (
            f"FunctionCalling(function={self.func_tool.function_name}, "
            f"arguments={self.arguments})"
        )


# File: lionagi/action/function_calling.py

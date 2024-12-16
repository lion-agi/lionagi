# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio

from lionagi.core.typing import Any, Field, PrivateAttr, override
from lionagi.libs.func.decorators import CallDecorator as cd
from lionagi.libs.func.types import tcall
from lionagi.settings import TimedFuncCallConfig

from .base import EventStatus, ObservableAction
from .tool import Tool


class FunctionCalling(ObservableAction):
    """Represents an action that calls a function with specified arguments.

    Encapsulates the complete function execution pipeline including:
    1. Pre-processing of input arguments
    2. Timed function execution
    3. Post-processing of results
    4. Optional result parsing
    5. Error handling and status tracking

    The execution is performed asynchronously and includes timing information
    and comprehensive error handling. The execution status, timing, and any
    errors are tracked and can be accessed after execution.

    Attributes:
        func_tool (Tool): Tool containing the function to be invoked and its
            processing pipeline configuration.
        arguments (dict[str, Any]): Arguments to pass to the function.
        function (str): Name of the function being called (derived from tool).
        _content_fields (list): Fields to include in log content section.
    """

    func_tool: Tool | None = Field(default=None, exclude=True)
    _content_fields: list = PrivateAttr(
        default=["execution_response", "arguments", "function"]
    )
    arguments: dict[str, Any] | None = None
    function: str | None = None

    def __init__(
        self,
        func_tool: Tool,
        arguments: dict[str, Any],
        timed_config: dict | TimedFuncCallConfig = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a FunctionCalling instance.

        Args:
            func_tool: Tool containing the function to invoke and its
                processing pipeline configuration.
            arguments: Arguments to pass to the function.
            timed_config: Configuration for timing and retries.
                If None, uses default config.
            **kwargs: Additional keyword arguments for timed config.
        """
        super().__init__(timed_config=timed_config, **kwargs)
        self.func_tool = func_tool
        self.arguments = arguments or {}
        self.function = self.func_tool.function_name

    @override
    async def invoke(self) -> Any:
        """Asynchronously invokes the function with stored arguments.

        Executes the complete function pipeline:
        1. Pre-processes arguments using tool's pre_processor if defined
        2. Executes function with timing and retry logic
        3. Post-processes result using tool's post_processor if defined
        4. Parses result using tool's parser if defined
        5. Tracks execution status, timing, and any errors

        Returns:
            The final processed result of the function execution.
            If execution fails, returns None and sets error information.

        Note:
            - All processing steps (pre/post/parse) are optional
            - Timing information is stored in execution_time
            - Errors are stored in execution_error
            - Raw response is stored in execution_response
            - Final status is stored in status
        """
        start = asyncio.get_event_loop().time()
        try:
            # Create inner function with pre/post processing
            @cd.pre_post_process(
                preprocess=self.func_tool.pre_processor,
                postprocess=self.func_tool.post_processor,
                preprocess_kwargs=self.func_tool.pre_processor_kwargs or {},
                postprocess_kwargs=self.func_tool.post_processor_kwargs or {},
            )
            async def _inner(**kwargs) -> Any:
                """Inner function that handles the actual execution.

                Applies timing and retry logic through tcall, and handles
                special case of timing information in result tuple.
                """
                config = self._timed_config.to_dict()
                result = await tcall(
                    self.func_tool.function, **kwargs, **config
                )
                # Handle tuple result from tcall when retry_timing is True
                if isinstance(result, tuple) and len(result) == 2:
                    return result[0]  # Return just the result, not timing info
                return result

            # Execute function with pre/post processing
            result = await _inner(**self.arguments)
            self.execution_response = result
            self.execution_time = asyncio.get_event_loop().time() - start
            self.status = EventStatus.COMPLETED

            # Apply parser if defined
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
            return None

    def __str__(self) -> str:
        """Returns a string representation of the function call.

        Returns:
            A string in the format "function_name(arguments)".
        """
        return f"{self.func_tool.function_name}({self.arguments})"

    def __repr__(self) -> str:
        """Returns a detailed string representation of the function call.

        Returns:
            A string containing the class name and key attributes.
        """
        return (
            f"FunctionCalling(function={self.func_tool.function_name}, "
            f"arguments={self.arguments})"
        )


__all__ = ["FunctionCalling"]

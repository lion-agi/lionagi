from typing import Any

from lionabc import EventStatus
from lionfuncs import CallDecorator as cd
from lionfuncs import tcall
from pydantic import Field, PrivateAttr
from typing_extensions import override

from lion_core.action.base import ObservableAction
from lion_core.action.tool import Tool
from lion_core.setting import TimedFuncCallConfig


class FunctionCalling(ObservableAction):
    """Represents an action that calls a function with specified arguments.

    Encapsulates a function call, including pre-processing, invocation,
    and post-processing steps. Designed to be executed asynchronously.

    Attributes:
        func_tool (Tool): Tool containing the function to be invoked.
        arguments (dict[str, Any]): Arguments for the function invocation.
        function_name (str | None): Name of the function to be called.
    """

    func_tool: Tool | None = Field(default=None, exclude=True)
    _content_fields: list = PrivateAttr(
        default=["execution_response", "arguments", "function_name"]
    )
    arguments: dict[str, Any] | None = None
    function_name: str | None = None

    def __init__(
        self,
        func_tool: Tool,
        arguments: dict[str, Any],
        timed_config: dict | TimedFuncCallConfig | None = None,
        **kwargs: Any,
    ) -> None:
        """
        kwargs for timed config
        """
        super().__init__(timed_config=timed_config, **kwargs)
        self.func_tool = func_tool
        self.arguments = arguments or {}
        self.function_name = self.func_tool.function_name

    @override
    async def invoke(self) -> Any | None:
        """Asynchronously invokes the function with stored arguments.

        Handles function invocation, applying pre/post-processing steps.
        If a parser is defined, it's applied to the result before returning.

        Returns:
            Any: Result of the function call, possibly processed.

        Raises:
            Exception: If function call or processing steps fail.
        """

        @cd.pre_post_process(
            preprocess=self.func_tool.pre_processor,
            preprocess_kwargs=self.func_tool.pre_processor_kwargs,
        )
        async def _inner(**kwargs) -> tuple[Any, Any | float]:
            kwargs["retry_timing"] = True
            result, elp = await tcall(self.func_tool.function, **kwargs)
            if self.func_tool.post_processor:
                kwargs = self.func_tool.post_processor_kwargs or {}
                kwargs = {
                    **kwargs,
                    **self._timed_config.to_dict(),
                    "retry_timing": True,
                }
                result, elp2 = await tcall(
                    self.func_tool.post_processor, result, **kwargs
                )
                elp += elp2
            return result, elp

        try:
            result, elp = await _inner(**self.arguments)
            self.execution_response = result
            self.execution_time = elp
            self.status = EventStatus.COMPLETED

            if self.func_tool.parser is not None:
                result = self.func_tool.parser(result)

            await self.alog()
            return result

        except Exception as e:
            self.status = EventStatus.FAILED
            self.execution_error = str(e)
            await self.alog()

    def __str__(self) -> str:
        """Returns a string representation of the function call."""
        return f"{self.func_tool.function_name}({self.arguments})"

    def __repr__(self) -> str:
        """Returns a detailed string representation of the function call."""
        return (
            f"FunctionCalling(function={self.func_tool.function_name}, "
            f"arguments={self.arguments})"
        )


__all__ = ["FunctionCalling"]
# File: lion_core/action/function_calling.py

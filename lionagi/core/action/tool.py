from collections.abc import Callable
from typing import Any, Dict, List, Union

from pydantic import Field, field_serializer

from lionagi.core.collections.abc import Actionable
from lionagi.core.generic.node import Node
from lionagi.libs.ln_func_call import call_handler

from .function_calling import FunctionCalling


class Tool(Node, Actionable):
    """
    Class representing a Tool with capabilities for pre-processing, post-processing,
    and parsing function results.

    Attributes:
        function (Callable): The callable function or capability of the tool.
        schema_ (Union[Dict, None]): Schema in OpenAI format.
        pre_processor (Union[Callable, None]): Function to preprocess input arguments.
        pre_processor_kwargs (Union[Dict, None]): Keyword arguments for the pre-processor.
        post_processor (Union[Callable, None]): Function to post-process the result.
        post_processor_kwargs (Union[Dict, None]): Keyword arguments for the post-processor.
        parser (Union[Callable, None]): Function to parse the result to a JSON serializable format.
    """

    function: Callable = Field(
        ...,
        description="The callable function or capability of the tool.",
    )

    schema_: dict | None = Field(
        None,
        description="Schema in OpenAI format.",
    )

    pre_processor: Callable | None = None
    pre_processor_kwargs: dict | None = None

    post_processor: Callable | None = None
    post_processor_kwargs: dict | None = None

    parser: Callable | None = None  # Parse result to JSON serializable format

    @field_serializer("function", check_fields=False)
    def serialize_func(self, func: Callable) -> str:
        """
        Serialize the function for storage or transmission.

        Args:
            func (Callable): The function to serialize.

        Returns:
            str: The name of the function.
        """
        return func.__name__

    @property
    def name(self) -> str:
        """
        Get the name of the function from the schema.

        Returns:
            str: The name of the function.
        """
        return self.schema_["function"]["name"]

    async def invoke(self, kwargs: dict = {}) -> Any:
        """
        Invoke the tool's function with optional pre-processing and post-processing.

        Args:
            kwargs (Dict): The arguments to pass to the function.

        Returns:
            Any: The result of the function call.
        """
        if self.pre_processor:
            pre_process_kwargs = self.pre_processor_kwargs or {}
            kwargs = await call_handler(
                self.pre_processor(kwargs, **pre_process_kwargs)
            )
            if not isinstance(kwargs, dict):
                raise ValueError("Pre-processor must return a dictionary.")

        func_call_ = FunctionCalling(function=self.function, arguments=kwargs)
        try:
            result = await func_call_.invoke()
        except Exception:
            return None

        if self.post_processor:
            post_process_kwargs = self.post_processor_kwargs or {}
            result = await call_handler(
                self.post_processor(result, **post_process_kwargs)
            )

        return result if not self.parser else self.parser(result)


TOOL_TYPE = Union[bool, Tool, str, list[Union[Tool, str, dict]], dict]

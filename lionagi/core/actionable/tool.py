"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Callable, Union, List, Dict, Any
from pydantic import Field, field_serializer
from lionagi.os.lib import ucall
from lionagi.os.collections.abc import Actionable
from lionagi.os.collections import Node
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

    schema_: Union[Dict, None] = Field(
        None,
        description="Schema in OpenAI format.",
    )

    pre_processor: Union[Callable, None] = None
    pre_processor_kwargs: Union[Dict, None] = None

    post_processor: Union[Callable, None] = None
    post_processor_kwargs: Union[Dict, None] = None

    parser: Union[Callable, None] = None  # Parse result to JSON serializable format

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

    async def invoke(self, kwargs: Dict = {}) -> Any:
        """
        Invoke the tool's function with optional pre-processing and post-processing.

        Args:
            kwargs (Dict): The arguments to pass to the function.

        Returns:
            Any: The result of the function call.
        """
        if self.pre_processor:
            pre_process_kwargs = self.pre_processor_kwargs or {}
            kwargs = await ucall(self.pre_processor(kwargs, **pre_process_kwargs))
            if not isinstance(kwargs, dict):
                raise ValueError("Pre-processor must return a dictionary.")

        func_call_ = FunctionCalling(function=self.function, arguments=kwargs)
        try:
            result = await func_call_.invoke()
        except Exception:
            return None

        if self.post_processor:
            post_process_kwargs = self.post_processor_kwargs or {}
            result = await ucall(self.post_processor(result, **post_process_kwargs))

        return result if not self.parser else self.parser(result)


TOOL_TYPE = Union[bool, Tool, str, List[Union[Tool, str, Dict]], Dict]

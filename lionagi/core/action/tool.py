# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from datetime import datetime

from pydantic import field_serializer, field_validator

from lionagi.core.generic.types import Element
from lionagi.core.typing import Any, Callable, Field, Literal, override
from lionagi.libs.parse import function_to_schema, to_list


class Tool(Element):
    """Represents a callable tool with pre/post-processing capabilities.

    A Tool wraps a function with optional pre-processing, post-processing,
    and result parsing capabilities. It also maintains a schema describing
    the function's interface in OpenAI function calling format.

    The processing pipeline consists of:
    1. Pre-processor: Transforms input arguments before function call
    2. Function: The actual function being called
    3. Post-processor: Transforms function result
    4. Parser: Converts result to JSON serializable format

    Each processing step is optional and can be configured independently.
    The schema is automatically generated from the function's signature
    and docstring unless explicitly provided.

    Attributes:
        function: The callable function of the tool.
        schema_: Schema of the function in OpenAI format.
        pre_processor: Optional function to preprocess input arguments.
        pre_processor_kwargs: Optional kwargs for the pre-processor.
        post_processor: Optional function to post-process the result.
        post_processor_kwargs: Optional kwargs for the post-processor.
        parser: Optional function to parse result to JSON format.
    """

    function: Callable[..., Any] = Field(
        ...,
        description="The callable function of the tool.",
    )
    schema_: dict[str, Any] | None = Field(
        default=None,
        description="Schema of the function in OpenAI format.",
    )
    pre_processor: Callable[[Any], Any] | None = Field(
        default=None,
        description="Function to preprocess input arguments.",
    )
    pre_processor_kwargs: dict[str, Any] | None = Field(
        default=None,
        description="Keyword arguments for the pre-processor.",
    )
    post_processor: Callable[[Any], Any] | None = Field(
        default=None,
        description="Function to post-process the result.",
    )
    post_processor_kwargs: dict[str, Any] | None = Field(
        default=None,
        description="Keyword arguments for the post-processor.",
    )
    parser: Callable[[Any], Any] | None = Field(
        default=None,
        description="Function to parse result to JSON serializable format.",
    )

    @override
    def __init__(self, **data: Any) -> None:
        """Initialize a Tool instance.

        If schema_ is not provided, automatically generates it from the
        function's signature and docstring.

        Args:
            **data: Keyword arguments to initialize the Tool instance.
        """
        super().__init__(**data)
        if self.schema_ is None:
            self.schema_ = function_to_schema(self.function)

    @field_validator("function")
    def _validate_function(cls, v: Any) -> Callable[..., Any]:
        if not callable(v):
            raise ValueError("Function must be callable.")
        if not hasattr(v, "__name__"):
            raise ValueError("Function must have a name.")
        return v

    @field_serializer(
        "function",
        "pre_processor",
        "post_processor",
        "parser",
        "pre_processor_kwargs",
        "post_processor_kwargs",
    )
    def serialize_field(self, v: Any) -> str | None:
        """Serialize various fields of the Tool class.

        Handles serialization of callable functions and dictionaries:
        - Functions are serialized to their names
        - Dictionaries are serialized to JSON strings
        - Other values are returned as None

        Args:
            v: The value to serialize.

        Returns:
            str: Serialized representation of the value.
            None: If value cannot be serialized.
        """
        if callable(v):
            return v.__name__
        elif isinstance(v, dict):
            return json.dumps(v)
        return None

    @property
    def function_name(self) -> str:
        """Get the name of the function from the schema.

        Returns:
            str: The name of the function as defined in the schema.
        """
        return self.schema_["function"]["name"]

    @override
    def __str__(self) -> str:
        """Return a string representation of the Tool.

        Includes class name, ID, timestamp, and schema for debugging
        and logging purposes.

        Returns:
            str: A detailed string representation of the Tool.
        """
        timestamp_str = datetime.fromtimestamp(self.timestamp).isoformat(
            timespec="minutes"
        )
        return (
            f"{self.class_name()}(ln_id={self.ln_id[:6]}.., "
            f"timestamp={timestamp_str}), "
            f"schema_={json.dumps(self.schema_, indent=4)}"
        )


def func_to_tool(
    func_: Callable[..., Any] | list[Callable[..., Any]],
    parser: Callable[[Any], Any] | list[Callable[[Any], Any]] | None = None,
    docstring_style: Literal["google", "rest"] = "google",
    **kwargs,
) -> list[Tool]:
    """Convert functions to Tool objects.

    Helper function to create Tool instances from callable functions.
    Supports both single functions and lists of functions, with optional
    result parsers for each function.

    Args:
        func_: Single function or list of functions to convert.
        parser: Optional parser(s) for function results. If provided for
            multiple functions, must match length of func_ list.
        docstring_style: Style of docstring parsing for schema generation.
            Supports 'google' or 'rest' format.
        **kwargs: Additional keyword arguments for Tool constructor.

    Returns:
        list[Tool]: List of Tool objects created from the functions.

    Raises:
        ValueError: If number of parsers doesn't match number of functions.

    Example:
        >>> def my_func(x: int) -> str:
        ...     '''Convert int to string.'''
        ...     return str(x)
        >>> tools = func_to_tool(my_func)
        >>> assert len(tools) == 1
        >>> assert isinstance(tools[0], Tool)
    """
    funcs = to_list(func_)
    parsers = to_list(parser)

    if parser and len(funcs) != len(parsers):
        raise ValueError("Length of parser must match length of func, ")

    tools = []
    for idx, func in enumerate(funcs):
        tool = Tool(
            function=func,
            schema_=function_to_schema(func, style=docstring_style),
            parser=parsers[idx] if parser else None,
            **kwargs,
        )
        tools.append(tool)

    return tools


__all__ = ["Tool", "func_to_tool"]

import json
from collections.abc import Callable
from datetime import datetime
from typing import Any, Literal

from lionfuncs import function_to_schema, to_list
from pydantic import Field, field_serializer, field_validator
from typing_extensions import override

from lion_core.generic.element import Element


class Tool(Element):
    """Represents a callable tool with pre/post-processing capabilities.

    Attributes:
        function: The callable function of the tool.
        schema_: Schema of the function in OpenAI format.
        pre_processor: Function to preprocess input arguments.
        pre_processor_kwargs: Keyword arguments for the pre-processor.
        post_processor: Function to post-process the result.
        post_processor_kwargs: Keyword arguments for the post-processor.
        parser: Function to parse the result to JSON serializable format.
    """

    function: Callable[..., Any] = Field(
        ...,
        description="The callable function of the tool.",
    )
    schema_: dict[str, Any] | None = Field(
        default=None,
        description="Schema of the function in OpenAI format.",
    )
    pre_processor: Callable[..., dict[str, Any]] | None = Field(
        default=None,
        description="Function to preprocess input arguments.",
    )
    pre_processor_kwargs: dict[str, Any] | None = Field(
        default=None,
        description="Keyword arguments for the pre-processor.",
    )
    post_processor: Callable[..., Any] | None = Field(
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

        Args:
            v: The value to serialize.

        Returns:
            Serialized representation of the value, or None if not applicable.
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
            The name of the function.
        """
        return self.schema_["function"]["name"]

    @override
    def __str__(self) -> str:
        """Return a string representation of the Tool.

        Returns:
            A string representation of the Tool.
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

    Args:
        func_: The function(s) to convert into tool(s).
        parser: Parser(s) to associate with the function(s).
        docstring_style: The style of the docstring parser to use.
        **kwargs: Additional keyword arguments for the Tool constructor.

    Returns:
        A list of Tool objects created from the provided function(s).

    Raises:
        ValueError: If the number of parsers doesn't match the number of
            functions.
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
# File: lion_core/action/tool.py

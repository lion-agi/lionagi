# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect
import json
from collections.abc import Callable
from typing import Any, Self, TypeAlias, override

from pydantic import Field, field_serializer, field_validator, model_validator

from lionagi.libs.schema.function_to_schema import function_to_schema

from ..generic.element import Element

__all__ = (
    "Tool",
    "func_to_tool",
    "FuncTool",
    "FuncToolRef",
    "ToolRef",
)


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

    func_callable: Callable[..., Any]
    tool_schema: dict[str, Any] | None = None
    preprocessor: Callable[[Any], Any] | None = Field(
        None
    )  # should in take arguments and return processed kwargs for the function, the function calling arguments should be first positional argument of the preprocessor
    preprocessor_kwargs: dict[str, Any] = Field(default_factory=dict)
    postprocessor: Callable[[Any], Any] | None = Field(
        None
    )  # should intake function output and return a processed output, the function output should be the first positional argument of the postprocessor
    postprocessor_kwargs: dict[str, Any] = Field(default_factory=dict)
    strict_func_call: bool = Field(False, exclude=True)

    @field_serializer("preprocessor_kwargs", "postprocessor_kwargs")
    def _serialize_kwargs(self, v: Any) -> str:
        try:
            return json.dumps(v)
        except TypeError:
            return {}

    @field_serializer("preprocessor", "postprocessor", "func_callable")
    def _serialize_processor(self, v: Any) -> str:
        if v is None:
            return None
        return v.__name__

    @model_validator(mode="after")
    def validate_tool_schema(self) -> Self:
        if self.tool_schema is None:
            self.tool_schema = function_to_schema(self.func_callable)
        return self

    @field_validator("func_callable")
    def _validate_function(cls, v: Any) -> Callable[..., Any]:
        if not callable(v):
            raise ValueError("Function must be callable.")
        if not hasattr(v, "__name__"):
            raise ValueError("Function must have a name.")
        return v

    @property
    def function(self) -> str:
        """Get the name of the function from the schema.

        Returns:
            str: The name of the function as defined in the schema.
        """
        return self.tool_schema["function"]["name"]

    @override
    def __str__(self) -> str:
        """Return a string representation of the Tool.

        Includes class name, ID, timestamp, and schema for debugging
        and logging purposes.

        Returns:
            str: A detailed string representation of the Tool.
        """
        timestamp_str = self.created_datetime.strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"{self.class_name()}(id={str(self.id)[:6]}.., "
            f"created_timestamp={timestamp_str}), "
            f"tool_schema={json.dumps(self.tool_schema, indent=4)}"
        )

    @property
    def required_fields(self) -> set[str]:
        return set(self.tool_schema["function"]["required_fields"])

    @property
    def minimum_acceptable_fields(self) -> set[str]:
        try:
            a = {
                k
                for k, v in inspect.signature(
                    self.func_callable
                ).parameters.items()
                if v.default == inspect.Parameter.empty
            }
            if "kwargs" in a:
                a.remove("kwargs")
            if "args" in a:
                a.remove("args")
            return a
        except Exception:
            return set()


FuncTool: TypeAlias = Tool | Callable[..., Any]
FuncToolRef: TypeAlias = FuncTool | str
ToolRef: TypeAlias = FuncToolRef | list[FuncToolRef] | bool

# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Defines the `Tool` class, which wraps a Python callable (function/method)
with optional pre/post-processing and schema auto-generation. Also includes
type aliases for function references.
"""

import inspect
from collections.abc import Callable
from typing import Any, TypeAlias

from pydantic import Field, field_validator, model_validator
from typing_extensions import Self

from lionagi.libs.schema.function_to_schema import function_to_schema
from lionagi.libs.validate.common_field_validators import validate_callable
from lionagi.protocols.generic.element import Element

__all__ = (
    "Tool",
    "func_to_tool",
    "FuncTool",
    "FuncToolRef",
    "ToolRef",
)


class Tool(Element):
    """
    Wraps a callable function with optional:
      - Preprocessing of arguments,
      - Postprocessing of results,
      - Strict or partial argument matching.

    `tool_schema` is auto-generated from the function signature if not provided.
    """

    func_callable: Callable[..., Any] = Field(
        ...,  # ... indicates required field
        description="The callable function to be wrapped by the tool",
        exclude=True,
    )

    tool_schema: dict[str, Any] | None = Field(
        default=None,
        description="Schema describing the function's parameters and structure",
    )

    request_options: type | None = Field(
        default=None,
        description="Optional Pydantic model for validating the function's input",
    )

    preprocessor: Callable[[Any], Any] | None = Field(
        default=None,
        description="Optional function for preprocessing inputs before execution",
        exclude=True,
    )

    preprocessor_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Keyword arguments passed to the preprocessor function",
        exclude=True,
    )

    postprocessor: Callable[[Any], Any] | None = Field(
        default=None,
        description="Optional function for postprocessing outputs after execution",
        exclude=True,
    )

    postprocessor_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Keyword arguments passed to the postprocessor function",
        exclude=True,
    )

    strict_func_call: bool = Field(
        default=False,
        description="Whether to enforce strict validation of function parameters",
    )

    @field_validator("func_callable", mode="before")
    def _validate_func_callable(cls, value: Any) -> Callable[..., Any]:
        return validate_callable(
            cls, value, undefind_able=False, check_name=True
        )

    @model_validator(mode="after")
    def _validate_tool_schema(self) -> Self:
        if self.tool_schema is None:
            self.tool_schema = function_to_schema(
                self.func_callable, request_options=self.request_options
            )

        return self

    @property
    def function(self) -> str:
        """Return the function name from the auto-generated schema."""
        return self.tool_schema["function"]["name"]

    @property
    def required_fields(self) -> set[str]:
        """Return the set of required parameter names from the schema."""
        return set(self.tool_schema["function"]["parameters"]["required"])

    @property
    def minimum_acceptable_fields(self) -> set[str]:
        """
        Return the set of parameters that have no default values,
        ignoring `*args` or `**kwargs`.
        """
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        """This is not implemented, as Tools are not typically created from arbitrary dicts."""
        raise NotImplementedError("`Tool.from_dict` is not supported.")

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the Tool to a dict, including the `function` name.

        Returns:
            dict[str, Any]: The dictionary form (excluding callables).
        """
        dict_ = super().to_dict()
        dict_["function"] = self.function
        return dict_


FuncTool: TypeAlias = Tool | Callable[..., Any]
"""Represents either a `Tool` instance or a raw callable function."""

FuncToolRef: TypeAlias = FuncTool | str
"""
A reference to a function-based tool, by either the actual object,
the raw callable, or the function name as a string.
"""

ToolRef: TypeAlias = FuncToolRef | list[FuncToolRef] | bool
"""
Used for specifying one or more tool references, or a boolean
indicating 'all' or 'none'.
"""


def func_to_tool(func: Callable[..., Any], **kwargs) -> Tool:
    """
    Convenience function that wraps a raw function in a `Tool`.

    Args:
        func (Callable[..., Any]): The function to wrap.
        **kwargs: Additional arguments passed to the `Tool` constructor.

    Returns:
        Tool: A new Tool instance wrapping `func`.
    """
    return Tool(func_callable=func, **kwargs)


# File: lionagi/operatives/action/tool.py

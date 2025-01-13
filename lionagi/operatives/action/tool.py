# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect
from collections.abc import Callable
from typing import Any, Self, TypeAlias

from pydantic import Field, field_validator, model_validator

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
    """A class for handling function calls with schema validation and processing.

    This class wraps callable objects with optional pre and post processing,
    schema validation, and provides utility methods for function inspection.
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
            self.tool_schema = function_to_schema(self.func_callable)
        return self

    @property
    def function(self) -> str:
        """Get the name of the function from the schema.

        Returns:
            str: The name of the function as defined in the schema.
        """
        return self.tool_schema["function"]["name"]

    @property
    def required_fields(self) -> set[str]:
        """Get the required fields from the schema.

        Returns:
            set[str]: Set of required field names.
        """
        return set(self.tool_schema["function"]["parameters"]["required"])

    @property
    def minimum_acceptable_fields(self) -> set[str]:
        """Get the minimum required fields from function signature.

        Returns:
            set[str]: Set of minimum required field names.
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
        raise NotImplementedError("Tool.from_dict is not implemented.")

    def to_dict(self) -> dict[str, Any]:
        """Convert Tool instance to dictionary.

        Returns:
            dict[str, Any]: Dictionary representation of the Tool.
        """
        dict_ = super().to_dict()
        dict_["function"] = self.function
        return dict_


FuncTool: TypeAlias = Tool | Callable[..., Any]
FuncToolRef: TypeAlias = FuncTool | str
ToolRef: TypeAlias = FuncToolRef | list[FuncToolRef] | bool

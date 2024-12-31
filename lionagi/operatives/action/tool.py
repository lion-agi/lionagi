# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect
from collections.abc import Callable
from typing import Any, Self, TypeAlias

from pydantic import Field, field_validator, model_validator

from lionagi.libs.schema.function_to_schema import function_to_schema
from lionagi.protocols.types import Element

__all__ = (
    "Tool",
    "func_to_tool",
    "FuncTool",
    "FuncToolRef",
    "ToolRef",
)


class Tool(Element):

    func_callable: Callable[..., Any] = Field(exclude=True)
    tool_schema: dict[str, Any] | None = None
    preprocessor: Callable[[Any], Any] | None = Field(None, exclude=True)
    preprocessor_kwargs: dict[str, Any] = Field(
        default_factory=dict, exclude=True
    )
    postprocessor: Callable[[Any], Any] | None = Field(None, exclude=True)
    postprocessor_kwargs: dict[str, Any] = Field(
        default_factory=dict, exclude=True
    )
    strict_func_call: bool = False

    @field_validator("func_callable", mode="before")
    def validate_func_callable(cls, value: Any) -> Callable[..., Any]:
        if not callable(value):
            raise ValueError("Function must be callable.")
        if not hasattr(value, "__name__"):
            raise ValueError("Function must have a name.")
        return value

    @model_validator(mode="after")
    def validate_tool_schema(self) -> Self:
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        raise NotImplementedError("Tool.from_dict is not implemented.")

    def to_dict(self) -> dict[str, Any]:
        dict_ = super().to_dict()
        dict_["function"] = self.function
        return dict_


FuncTool: TypeAlias = Tool | Callable[..., Any]
FuncToolRef: TypeAlias = FuncTool | str
ToolRef: TypeAlias = FuncToolRef | list[FuncToolRef] | bool

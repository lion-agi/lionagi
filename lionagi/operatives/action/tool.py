# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect
from collections.abc import Callable
from typing import Any, TypeAlias

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

    def __init__(
        self,
        func_callable: Callable[..., Any],
        tool_schema: dict[str, Any] | None = None,
        preprocessor: Callable[[Any], Any] | None = None,
        preprocessor_kwargs: dict[str, Any] = {},
        postprocessor: Callable[[Any], Any] | None = None,
        postprocessor_kwargs: dict[str, Any] = {},
        strict_func_call: bool = False,
    ):
        if not callable(func_callable):
            raise ValueError("Function must be callable.")
        if not hasattr(func_callable, "__name__"):
            raise ValueError("Function must have a name.")

        super().__init__()

        self.func_callable = func_callable
        self.tool_schema = tool_schema
        self.preprocessor = preprocessor
        self.preprocessor_kwargs = preprocessor_kwargs
        self.postprocessor = postprocessor
        self.postprocessor_kwargs = postprocessor_kwargs
        self.strict_func_call = strict_func_call

        if self.tool_schema is None:
            self.tool_schema = function_to_schema(self.func_callable)

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


FuncTool: TypeAlias = Tool | Callable[..., Any]
FuncToolRef: TypeAlias = FuncTool | str
ToolRef: TypeAlias = FuncToolRef | list[FuncToolRef] | bool

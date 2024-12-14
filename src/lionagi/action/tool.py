# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Awaitable, Callable
from typing import Any, TypeAlias

from pydantic import Field, field_serializer, model_validator
from typing_extensions import Self

from lionagi.libs.async_utils import TCallParams
from lionagi.libs.parse import function_to_schema, to_dict

from ..protocols.models import BaseAutoModel

__all__ = ("Tool", "FuncTool")


AsyncCallable: TypeAlias = Callable[..., Awaitable[Any]]
Schema: TypeAlias = dict[str, Any]


class Tool(BaseAutoModel):
    """Wraps an async callable with schema validation and execution parameters."""

    function: Callable | AsyncCallable = Field(
        ..., description="The async callable function of the tool."
    )
    schema_: Schema | None = Field(
        default=None, description="Optional schema of the function."
    )
    tcall: TCallParams | None = Field(
        default=None, description="Optional parameters for tcall."
    )

    @field_serializer("tcall")
    def _serialize_tcall(self, value: TCallParams) -> dict[str, Any]:
        """Serialize tcall to dictionary format."""
        return value.to_dict()

    @model_validator(mode="after")
    def _validate_schema(self) -> Self:
        """Validate and normalize schema after model initialization."""
        if not self.schema_:
            self.schema_ = function_to_schema(self.function).to_dict()
            return

        if hasattr(self.schema_, "to_dict"):
            self.schema_ = self.schema_.to_dict()
        if not isinstance(self.schema_, dict):
            self.schema_ = to_dict(self.schema_)

        if not self.tcall:
            self.tcall = TCallParams()
        self.tcall.timing = False
        self.tcall.function = self.function

        return self

    @property
    def function_name(self) -> str:
        """Get function name of the wrapped callable."""
        return self.function.__name__

    def __str__(self) -> str:
        """Return a string representation of the Tool."""
        return f"Tool(name={self.function_name})"


FuncTool = Tool | Callable[..., Awaitable[Any]]

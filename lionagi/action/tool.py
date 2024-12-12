# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import Field, model_validator
from typing_extensions import Self

from lionagi.libs.async_utils import TCallParams
from lionagi.libs.parse import function_to_schema, to_dict

from ..protocols.models import BaseAutoModel


class Tool(BaseAutoModel):

    function: Callable[..., Awaitable[Any]] = Field(
        ..., description="The async callable function of the tool."
    )
    schema_: dict | None = Field(
        default=None, description="Optional schema of the function."
    )
    tcall: TCallParams | None = Field(
        default=None, description="Optional parameters for tcall."
    )

    @model_validator(mode="after")
    def _validate_schema(self) -> Self:
        if not self.schema_:
            self.schema_ = function_to_schema(self.function).to_dict()
            return
        if not isinstance(self.schema_, dict):
            self.schema_ = to_dict(self.schema_)
        if not self.tcall:
            self.tcall = TCallParams()
        self.tcall.timing = False
        self.tcall.function = self.function

        return self

    @property
    def function_name(self) -> str:
        """Return the name of the function."""
        return self.function.__name__

    def __str__(self) -> str:
        """Return a string representation of the Tool."""
        return f"Tool(name={self.function_name})"


FuncTool = Tool | Callable[..., Awaitable[Any]]

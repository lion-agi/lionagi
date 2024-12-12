# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from dataclasses import asdict, dataclass
from typing import Any, Self

PY_TYPE_TO_JSON = {
    "int": "integer",
    "str": "string",
    "bool": "boolean",
    "float": "number",
    "list": "array",
    "dict": "object",
}


class DataClass:

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(**data)


@dataclass
class CodeBlock(DataClass):
    lang: str
    code: str

    def __str__(self) -> str:
        return f"{self.lang}\n{self.code}\n"

    def __repr__(self) -> str:
        return f"CodeBlock(lang={self.lang!r}, code={self.code!r})"


@dataclass
class CodeResult(DataClass):
    exit_code: int
    output: str
    fp: str | None = None  # file path of the source code


@dataclass
class FunctionSchema:
    name: str
    description: str
    parameters: dict[str, Any]

    def to_dict(self) -> dict:
        return {
            "type": "function",
            "function": asdict(self),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        if "type" in data and data["type"] == "function":
            return cls(**data["function"])
        return cls(**data)

    def __str__(self) -> str:
        return str(self.to_dict())

    def __repr__(self) -> str:
        return f"FunctionSchema(name={self.name!r}, description={self.description!r})"

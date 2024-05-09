from enum import Enum
from typing import Any
from pydantic import field_validator
from ..generic.abc import Element, Field


class PackageCategory(str, Enum):
    TOOL = "tool"
    SERVICE = "service"
    MODEL = "model"
    NODE = "node"
    NODE_LIST = "node_list"
    NODE_ID = "node_id"
    START = "start"
    END = "end"
    CONDITION = "condition"


class Package(Element):

    category: PackageCategory = Field(
        None,
        title="Category",
        description="The category of the package.",
    )

    package: Any = Field(
        None,
        title="Package",
        description="The package to be delivered.",
    )

    @field_validator("category", mode="before")
    def validate_category(cls, value: Any):
        if value is None:
            raise ValueError("Package category cannot be None.")
        if isinstance(value, PackageCategory):
            value = value
        else:
            try:
                value = PackageCategory(value)
            except Exception as e:
                raise ValueError(f"Invalid value for category: {value}.") from e

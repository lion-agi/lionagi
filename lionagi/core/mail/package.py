from enum import Enum
from typing import Any
from pydantic import field_validator
from lionagi.core.collections.abc import Element, Field

from typing_extensions import deprecated

from lionagi.os.sys_utils import format_deprecated_msg


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.action.function_calling.FunctionCalling",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class PackageCategory(str, Enum):
    MESSAGE = "message"
    TOOL = "tool"
    IMODEL = "imodel"
    NODE = "node"
    NODE_LIST = "node_list"
    NODE_ID = "node_id"
    START = "start"
    END = "end"
    CONDITION = "condition"


class Package(Element):

    request_source: str | None = None

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
            return value
        else:
            try:
                return PackageCategory(value)
            except Exception as e:
                raise ValueError(f"Invalid value for category: {value}.") from e

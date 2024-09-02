from typing import Any
from pydantic import Field
from lionagi.core.collections.abc import Condition
from pydantic import BaseModel

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
class EdgeCondition(Condition, BaseModel):
    source: Any = Field(
        title="Source",
        description="The source for condition check",
    )

    class Config:
        """Model configuration settings."""

        extra = "allow"

from typing import Any

from pydantic import BaseModel, Field

from lionagi.core.collections.abc import Condition


class EdgeCondition(Condition, BaseModel):
    source: Any = Field(
        title="Source",
        description="The source for condition check",
    )

    class Config:
        """Model configuration settings."""

        extra = "allow"

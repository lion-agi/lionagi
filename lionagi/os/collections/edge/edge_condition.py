from typing import Any
from pydantic import Field
from ..abc import Condition
from pydantic import BaseModel


class EdgeCondition(Condition, BaseModel):
    source: Any = Field(
        title="Source",
        description="The source for condition check",
    )

    class Config:
        """Model configuration settings."""

        extra = "allow"

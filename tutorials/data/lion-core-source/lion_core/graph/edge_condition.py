from typing import Any

from lionabc import Condition
from pydantic import BaseModel, ConfigDict, Field


class EdgeCondition(BaseModel, Condition):
    """Represents a condition associated with an edge in the Lion framework.

    This class combines Condition characteristics with Pydantic's
    BaseModel for robust data validation and serialization.

    Attributes:
        source (Any): The source for condition evaluation.
    """

    source: Any = Field(
        default=None,
        title="Source",
        description="The source for condition evaluation",
    )

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )


__all__ = ["EdgeCondition"]

# File: lion_core/generic/edge_condition.py

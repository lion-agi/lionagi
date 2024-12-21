from enum import Enum
from typing import Any

from pydantic import Field

from lionagi.core.action.base import ObservableAction


class OperationType(str, Enum):
    INSTRUCT = "instruct"
    BRAINSTORM = "brainstorm"
    REFLECT = "reflect"
    PLAN = "plan"
    CRITIQUE = "critique"
    REASON = "reason"
    BACKTRACK = "backtrack"
    EVALUATE = "evaluate"
    JUDGE = "judge"
    ANALYZE = "analyze"
    REVIEW = "review"
    OTHER = "other"


class Task(ObservableAction):
    """
    Represents a single instruction or step to be executed
    by the strategy.
    """

    payload: Any = Field(..., description="Task data/payload")
    depends_on: Any = Field(
        None, description="Optional dependency on another task ID"
    )
    # Track the type of operation
    op_type: OperationType = Field(
        default=OperationType.OTHER, description="Type of operation"
    )

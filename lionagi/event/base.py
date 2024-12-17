from abc import ABC
from enum import Enum
from typing import Any

from pydantic import BaseModel

from lionagi.utils import DataClass, dataclass


@dataclass
class ExecutionResult(DataClass):
    execution_time: float
    execution_response: Any
    execution_error: str


class EventStatus(str, Enum):
    """Event execution status states."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Event(ABC):
    status: EventStatus = EventStatus.PENDING

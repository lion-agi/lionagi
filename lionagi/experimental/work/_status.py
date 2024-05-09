from enum import Enum

class WorkStatus(str, Enum):
    """Enum to represent different statuses of work."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
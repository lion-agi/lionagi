from dataclasses import dataclass


@dataclass
class StatusTracker:
    """
    Keeps track of various task statuses within a system.

    Attributes:
        num_tasks_started (int): The number of tasks that have been initiated.
        num_tasks_in_progress (int): The number of tasks currently being processed.
        num_tasks_succeeded (int): The number of tasks that have completed successfully.
        num_tasks_failed (int): The number of tasks that have failed.
        num_rate_limit_errors (int): The number of tasks that failed due to rate limiting.
        num_api_errors (int): The number of tasks that failed due to API errors.
        num_other_errors (int): The number of tasks that failed due to other errors.

    Examples:
        >>> tracker = StatusTracker()
        >>> tracker.num_tasks_started += 1
        >>> tracker.num_tasks_succeeded += 1
    """
    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_rate_limit_errors: int = 0
    num_api_errors: int = 0
    num_other_errors: int = 0

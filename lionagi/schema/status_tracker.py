from dataclasses import dataclass


# credit to OpenAI for the following object
@dataclass
class StatusTracker:
    """
    Class for keeping track of various task statuses.
    
    This class serves as a simple way to monitor different types of task
    outcomes and errors within a system. It uses dataclasses for easy
    creation and management of state.
    
    Attributes:
        num_tasks_started:
            The number of tasks that have been initiated.
        num_tasks_in_progress:
            The number of tasks currently being processed.
        num_tasks_succeeded:
            The number of tasks that have completed successfully.
        num_tasks_failed:
            The number of tasks that have failed.
        num_rate_limit_errors:
            The number of tasks that failed due to rate limiting.
        num_api_errors:
            The number of tasks that failed due to API errors.
        num_other_errors:
            The number of tasks that failed due to other errors.
    """
    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_rate_limit_errors: int = 0
    num_api_errors: int = 0
    num_other_errors: int = 0
    
# lionagi/strategies/operative.py

from typing import List

from pydantic import BaseModel

from lionagi.protocols.operatives.tasks import Task


class Strategy(BaseModel):
    """
    Represents a strategy-level 'operative' object that holds multiple operations (tasks).
    Integrates with the strategy system by exposing `instruct_models` for executors.
    """

    name: str
    description: str
    instruct_models: list[Task] = []

    def add_operation(self, task: Task) -> None:
        """Adds a new operation (task) to this operative."""
        self.instruct_models.append(task)

    def clear_operations(self) -> None:
        """Clears all operations."""
        self.instruct_models.clear()

    def list_operations(self) -> list[Task]:
        """Returns the list of current operations."""
        return self.instruct_models

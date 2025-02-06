import inspect
from collections.abc import Callable
from typing import Any

from pydantic import Field, field_validator

from lionagi.protocols.generic.event import Event, EventStatus
from lionagi.protocols.generic.log import Log
from lionagi.utils import to_dict

from .work import Work
from .work_function_node import WorkFunctionNode


class WorkTask(Event):
    """
    A class representing a work task that can be processed in multiple steps.

    This class extends Event to provide execution state tracking and event handling,
    while adding work-specific attributes for task management.

    Attributes:
        name (str | None): The name of the task.
        work_history (list[Work]): A list of works processed in this task.
        max_steps (int | None): The maximum number of works allowed in this task.
        current_work (Work | None): The current work in progress.
        current_func_node (WorkFunctionNode | None): The current function node being processed.
        post_processing (Callable | None): The post-processing function to be executed after completion.
    """

    name: str | None = Field(None, description="Name of the task")

    work_history: list[Work] = Field([], description="List of works processed")

    max_steps: int | None = Field(
        10, description="Maximum number of works allowed"
    )

    current_work: Work | None = Field(
        None, description="The current work in progress"
    )

    current_func_node: WorkFunctionNode | None = Field(
        None, description="The current function node being processed"
    )

    post_processing: Callable | None = Field(
        None,
        description="The post-processing function to be executed after completion",
    )

    @field_validator("max_steps", mode="before")
    def _validate_max_steps(cls, value):
        """
        Validates that max_steps is a positive integer.
        """
        if value <= 0:
            raise ValueError(
                "Invalid value: max_steps must be a positive integer."
            )
        return value

    @field_validator("post_processing", mode="before")
    def _validate_post_processing(cls, value):
        """
        Validates that post_processing is an asynchronous function.
        """
        if value is not None and not inspect.iscoroutinefunction((value)):
            raise ValueError("post_processing must be a async function")
        return value

    @property
    def available_steps(self):
        """
        Calculates the number of available steps left in the task.
        """
        return max(0, self.max_steps - len(self.work_history))

    def clone(self):
        """
        Creates a clone of the current WorkTask instance.
        """
        new_worktask = WorkTask(
            name=self.name,
            max_steps=self.max_steps,
            current_work=self.current_work,
            current_func_node=self.current_func_node,
        )
        for work in self.work_history:
            new_worktask.work_history.append(work)
        return new_worktask

    async def process(self, func_node: WorkFunctionNode) -> None:
        """
        Sets up the task with a function node and processes it.
        """
        self.current_func_node = func_node
        await self.invoke()

    async def invoke(self) -> None:
        """
        Processes the current work function node.
        """
        if self.current_func_node is None:
            raise ValueError("No function node set for processing")

        self.status = EventStatus.PROCESSING

        try:
            if self.current_work.status == "FAILED":
                self.status = EventStatus.FAILED
                self.execution.error = f"Work {self.current_work.ln_id} failed. Error: {self.current_work.error}"
                self.current_work = None
                self.execution.response = "FAILED"
            elif self.current_work.status == "COMPLETED":
                next_works = []
                if not self.current_func_node.relations["out"].is_empty():
                    for workedge in self.current_func_node.relations["out"]:
                        next_work = await workedge.forward(self)
                        if next_work is not None:
                            next_works.append(next_work)
                if len(next_works) == 0:
                    self.current_work = None
                    self.status = EventStatus.COMPLETED
                    if self.post_processing:
                        await self.post_processing(self)
                    self.execution.response = "COMPLETED"
                else:
                    return_tasks = []
                    for i in reversed(range(len(next_works))):
                        if i == 0:
                            self.current_work = next_works[i]
                            self.work_history.append(next_works[i])
                        else:
                            clone_task = self.clone()
                            clone_task.current_work = next_works[i]
                            clone_task.work_history.append(next_works[i])
                            return_tasks.append(clone_task)
                    self.execution.response = return_tasks

        except Exception as e:
            self.status = EventStatus.FAILED
            self.execution.error = str(e)

    async def stream(self) -> None:
        """
        Performs the task with streaming results.
        For now, we just call invoke since we don't need streaming.
        """
        await self.invoke()

    def to_log(self) -> Log:
        """Create a Log object summarizing this event."""
        return Log(
            content={
                "type": "WorkTask",
                "name": self.name,
                "current_work": (
                    self.current_work.ln_id if self.current_work else None
                ),
                "current_func": (
                    self.current_func_node.name
                    if self.current_func_node
                    else None
                ),
                "work_history": [w.ln_id for w in self.work_history],
                "status": str(self.status),
                "response": to_dict(self.execution.response),
                "error": self.execution.error,
            }
        )

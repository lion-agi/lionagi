import inspect
from collections.abc import Callable

from pydantic import Field, field_validator

from lionagi.core.collections.abc.component import Component
from lionagi.core.work.work import Work, WorkStatus


class WorkTask(Component):
    """
    A class representing a work task that can be processed in multiple steps.

    Attributes:
        name (str | None): The name of the task.
        status (WorkStatus): The current status of the task.
        status_note (str): A note for the task's current status.
        work_history (list[Work]): A list of works processed in this task.
        max_steps (int | None): The maximum number of works allowed in this task.
        current_work (Work | None): The current work in progress.
        post_processing (Callable | None): The post-processing function to be executed after the entire task is successfully completed.
    """

    name: str | None = Field(None, description="Name of the task")

    status: WorkStatus = Field(
        WorkStatus.PENDING, description="The current status of the task"
    )

    status_note: str = Field(None, description="Note for tasks current status")

    work_history: list[Work] = Field([], description="List of works processed")

    max_steps: int | None = Field(
        10, description="Maximum number of works allowed"
    )

    current_work: Work | None = Field(
        None, description="The current work in progress"
    )

    post_processing: Callable | None = Field(
        None,
        description="The post-processing function to be executed after the entire task has been successfully completed.",
    )

    @field_validator("max_steps", mode="before")
    def _validate_max_steps(cls, value):
        """
        Validates that max_steps is a positive integer.

        Args:
            value (int): The value to validate.

        Returns:
            int: The validated value.

        Raises:
            ValueError: If value is not a positive integer.
        """
        if value <= 0:
            raise ValueError(
                "Invalid value: max_steps must be a positive integer."
            )
        return value

    @field_validator("post_processing", mode="before")
    def _validate_prost_processing(cls, value):
        """
        Validates that post_processing is an asynchronous function.

        Args:
            value (Callable): The value to validate.

        Returns:
            Callable: The validated value.

        Raises:
            ValueError: If value is not an asynchronous function.
        """
        if value is not None and not inspect.iscoroutinefunction(value):
            raise ValueError("post_processing must be a async function")
        return value

    @property
    def available_steps(self):
        """
        Calculates the number of available steps left in the task.

        Returns:
            int: The number of available steps.
        """
        return max(0, self.max_steps - len(self.work_history))

    def clone(self):
        """
        Creates a clone of the current WorkTask instance.

        Returns:
            WorkTask: A new instance of WorkTask with the same attributes.
        """
        new_worktask = WorkTask(
            name=self.name,
            status=self.status,
            max_steps=self.max_steps,
            current_work=self.current_work,
        )
        for work in self.work_history:
            new_worktask.work_history.append(work)
        return new_worktask

    async def process(self, current_func_node):
        """
        Processes the current work function node.

        Args:
            current_func_node (WorkFunctionNode): The current function node being processed.

        Returns:
            str | list[WorkTask]: Returns "COMPLETED", "FAILED", or a list of new WorkTask instances if there are next works to process.
        """
        if self.current_work.status == WorkStatus.FAILED:
            self.status = WorkStatus.FAILED
            self.status_note = f"Work {self.current_work.ln_id} failed. Error: {self.current_work.error}"
            self.current_work = None
            return "FAILED"
        elif self.current_work.status == WorkStatus.COMPLETED:
            next_works = []
            if not current_func_node.relations["out"].is_empty():
                for workedge in current_func_node.relations["out"]:
                    next_work = await workedge.forward(self)
                    if next_work is not None:
                        next_works.append(next_work)
            if len(next_works) == 0:
                self.current_work = None
                self.status = WorkStatus.COMPLETED
                if self.post_processing:
                    await self.post_processing(self)
                return "COMPLETED"
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
                return return_tasks

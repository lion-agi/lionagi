import inspect
from collections.abc import Callable

from pydantic import Field, field_validator

from lionagi.core.collections.abc.concepts import Progressable
from lionagi.core.generic.edge import Edge
from lionagi.core.work.worker import Worker


class WorkEdge(Edge, Progressable):
    """
    Represents a directed edge between work tasks, responsible for transforming
    the result of one task into parameters for the next task.

    Attributes:
        convert_function (Callable): Function to transform the result of the previous
            work into parameters for the next work. This function must be decorated
            with the `worklink` decorator.
        convert_function_kwargs (dict): Additional parameters for the convert_function
            other than "from_work" and "from_result".
        associated_worker (Worker): The worker to which this WorkEdge belongs.
    """

    convert_function: Callable = Field(
        ...,
        description="Function to transform the result of the previous work into parameters for the next work.",
    )

    convert_function_kwargs: dict = Field(
        {},
        description='parameters for the worklink function other than "from_work" and "from_result"',
    )

    associated_worker: Worker = Field(
        ..., description="The worker to which this WorkEdge belongs."
    )

    @field_validator("convert_function", mode="before")
    def _validate_convert_funuction(cls, func):
        """
        Validates that the convert_function is decorated with the worklink decorator.

        Args:
            func (Callable): The function to validate.

        Returns:
            Callable: The validated function.

        Raises:
            ValueError: If the function is not decorated with the worklink decorator.
        """
        try:
            getattr(func, "_worklink_decorator_params")
            return func
        except:
            raise ValueError(
                "convert_function must be a worklink decorated function"
            )

    @property
    def name(self):
        """
        Returns the name of the convert_function.

        Returns:
            str: The name of the convert_function.
        """
        return self.convert_function.__name__

    async def forward(self, task):
        """
        Transforms the result of the current work into parameters for the next work
        and schedules the next work task.

        Args:
            task (Task): The task to process.

        Returns:
            Work: The next work task to be executed.

        Raises:
            StopIteration: If the task has no available steps left to proceed.
        """
        if task.available_steps == 0:
            task.status_note = (
                "Task stopped proceeding further as all available steps have been used up, "
                "but the task has not yet reached completion."
            )
            return
        func_signature = inspect.signature(self.convert_function)
        kwargs = self.convert_function_kwargs.copy()
        if "from_work" in func_signature.parameters:
            kwargs = {"from_work": task.current_work} | kwargs
        if "from_result" in func_signature.parameters:
            kwargs = {"from_result": task.current_work.result} | kwargs

        self.convert_function.auto_schedule = True
        next_work = await self.convert_function(
            self=self.associated_worker, **kwargs
        )
        return next_work

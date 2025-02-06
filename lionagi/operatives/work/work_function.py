import asyncio
import inspect
import time
from collections.abc import Callable
from typing import Any

from pydantic import Field, field_validator

from lionagi.protocols.generic.element import Element

from .worklog import WorkLog


class WorkFunction(Element):
    """
    A class representing a work function.

    This class extends Element to provide unique identification and timestamp tracking,
    while managing a callable function and its execution context.

    Attributes:
        assignment (str): The assignment description of the work function.
        function (Callable): The function to be performed.
        retry_kwargs (dict): The retry arguments for the function.
        worklog (WorkLog): The work log for the function.
        guidance (str): The guidance or documentation for the function.
    """

    assignment: str = Field(
        ..., description="The assignment description of the work function"
    )

    function: Callable = Field(..., description="The function to be performed")

    retry_kwargs: dict = Field(
        default_factory=dict,
        description="The retry arguments for the function",
    )

    guidance: str | None = Field(
        None, description="The guidance or documentation for the function"
    )

    worklog: WorkLog = Field(
        exclude=True,  # Exclude from serialization since it contains complex objects
        description="The work log for the function",
    )

    @field_validator("function")
    def validate_function(cls, value: Callable) -> Callable:
        """
        Validates that the function is a callable.

        Args:
            value (Callable): The function to validate.

        Returns:
            Callable: The validated function.

        Raises:
            ValueError: If the value is not callable.
        """
        if not callable(value):
            raise ValueError("function must be callable")
        return value

    def __init__(
        self,
        assignment: str,
        function: Callable,
        retry_kwargs: dict | None = None,
        guidance: str | None = None,
        capacity: int = 10,
        refresh_time: float = 1,
        **kwargs,
    ):
        """
        Initializes a WorkFunction instance.

        Args:
            assignment (str): The assignment description of the work function.
            function (Callable): The function to be performed.
            retry_kwargs (dict, optional): The retry arguments for the function.
            guidance (str, optional): The guidance or documentation for the function.
            capacity (int, optional): The capacity of the work queue batch processing.
                Defaults to 10.
            refresh_time (float, optional): The time interval to refresh the work log queue.
                Defaults to 1.
        """
        super().__init__(**kwargs)
        self.assignment = assignment
        self.function = function
        self.retry_kwargs = retry_kwargs or {}
        self.guidance = guidance or self.function.__doc__
        self.worklog = WorkLog(capacity=capacity, refresh_time=refresh_time)

    @property
    def name(self) -> str:
        """
        Gets the name of the function.

        Returns:
            str: The name of the function.
        """
        return self.function.__name__

    @property
    def execution_mode(self) -> bool:
        """
        Gets the execution mode of the work function's queue.

        Returns:
            bool: The execution mode of the work function's queue.
        """
        return self.worklog.queue.execution_mode

    def is_progressable(self) -> bool:
        """
        Checks if the work function is progressable.

        Returns:
            bool: True if the work function is progressable, otherwise False.
        """
        return bool(self.worklog.pending_work and not self.worklog.stopped)

    async def perform(self, *args: Any, **kwargs: Any) -> tuple[Any, float]:
        """
        Performs the work function with timing measurement.

        Args:
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            tuple[Any, float]: A tuple containing the result and execution duration.
        """
        kwargs = {**self.retry_kwargs, **kwargs}
        start_time = time.perf_counter()

        if inspect.iscoroutinefunction(self.function):
            result = await self.function(*args, **kwargs)
        else:
            result = self.function(*args, **kwargs)

        duration = time.perf_counter() - start_time
        return result, duration

    async def forward(self) -> None:
        """
        Forward the work log to work queue.
        """
        await self.worklog.forward()

    async def process(self) -> None:
        """
        Process the first capacity_size works in the work queue.
        """
        await self.worklog.queue.process()

    async def execute(self) -> None:
        """
        Starts the execution of the work function's queue.
        """
        asyncio.create_task(self.worklog.queue.execute())

    async def stop(self) -> None:
        """
        Stops the execution of the work function's queue.
        """
        await self.worklog.stop()

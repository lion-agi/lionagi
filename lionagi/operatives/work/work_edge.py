import inspect
from collections.abc import Callable
from typing import Any

from pydantic import Field, field_validator

from lionagi.protocols._concepts import Ordering
from lionagi.protocols.generic.event import EventStatus
from lionagi.protocols.generic.log import Log
from lionagi.protocols.graph import Edge
from lionagi.utils import to_dict

from .work import Work
from .worker import Worker


class WorkEdge(Edge, Ordering[Work]):
    """
    Represents a directed edge between work tasks, responsible for transforming
    the result of one task into parameters for the next task.

    This class extends Edge to provide graph connectivity and Ordering to manage
    the sequence of work transformations.

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
        description="Function to transform the result of the previous work into parameters for the next work",
    )

    convert_function_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description='Parameters for the worklink function other than "from_work" and "from_result"',
    )

    associated_worker: Worker = Field(
        ..., description="The worker to which this WorkEdge belongs"
    )

    @field_validator("convert_function", mode="before")
    def _validate_convert_function(cls, func: Callable) -> Callable:
        """
        Validates that the convert_function is decorated with the worklink decorator.
        """
        try:
            getattr(func, "_worklink_decorator_params")
            return func
        except AttributeError:
            raise ValueError(
                "convert_function must be a worklink decorated function"
            )

    @property
    def name(self) -> str:
        """
        Returns the name of the convert_function.
        """
        return self.convert_function.__name__

    async def forward(self, task: Any) -> Work | None:
        """
        Transforms the result of the current work into parameters for the next work
        and schedules the next work task.
        """
        if task.available_steps == 0:
            task.status = EventStatus.FAILED
            task.execution.error = (
                "Task stopped proceeding further as all available steps have been used up, "
                "but the task has not yet reached completion."
            )
            return None

        func_signature = inspect.signature(self.convert_function)
        kwargs = self.convert_function_kwargs.copy()

        if "from_work" in func_signature.parameters:
            kwargs = {"from_work": task.current_work} | kwargs
        if "from_result" in func_signature.parameters:
            kwargs = {
                "from_result": task.current_work.execution.response
            } | kwargs

        self.convert_function.auto_schedule = True
        next_work = await self.convert_function(
            self=self.associated_worker, **kwargs
        )
        return next_work

    def include(self, item: Work, /) -> None:
        """
        Include a work item in the edge's sequence.
        Required by Ordering protocol but not used in WorkEdge.
        """
        pass

    def exclude(self, item: Work, /) -> None:
        """
        Exclude a work item from the edge's sequence.
        Required by Ordering protocol but not used in WorkEdge.
        """
        pass

    def to_log(self) -> Log:
        """Create a Log object summarizing this edge."""
        return Log(
            content={
                "type": "WorkEdge",
                "id": str(self.id),
                "name": self.name,
                "convert_function": self.convert_function.__name__,
                "kwargs": to_dict(self.convert_function_kwargs),
                "worker": str(self.associated_worker.id),
                "head": str(self.head.id) if self.head else None,
                "tail": str(self.tail.id) if self.tail else None,
            }
        )

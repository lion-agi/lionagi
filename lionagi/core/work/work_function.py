from typing import Callable
from lionagi.libs.ln_func_call import rcall
from pydantic import Field

from ..generic.abc import Element
from .worklog import WorkLog


class WorkFunction(Element):

    assignment: str = Field(...)
    function: Callable = Field(...)
    retry_kwargs: dict = Field(None)
    guidance: str = Field(None)
    worklog: WorkLog = Field(None)

    def __init__(
        self, assignment, function, retry_kwargs=None, guidance=None, capacity=10
    ):
        self.assignment = assignment
        self.function = function
        self.retry_kwargs = retry_kwargs or {}
        self.worklog = WorkLog(capacity)
        self.guidance = guidance or self.function.__doc__

    @property
    def name(self):
        return self.function.__name__

    async def perform(self, *args, **kwargs):
        kwargs = {**self.retry_kwargs, **kwargs}
        return await rcall(self.function, *args, **kwargs)

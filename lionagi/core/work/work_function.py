from typing import Callable
from lionagi.libs.ln_func_call import rcall
from pydantic import Field

import asyncio
from ..generic.abc import Element
from .worklog import WorkLog


class WorkFunction:
    """
    A class representing a work function.

    Attributes:
        assignment (str): The assignment description of the work function.
        function (Callable): The function to be performed.
        retry_kwargs (dict): The retry arguments for the function.
        worklog (WorkLog): The work log for the function.
        guidance (str): The guidance or documentation for the function.
    """

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

    def is_progressable(self):
        return self.worklog.pending_work and not self.worklog.stopped

    async def perform(self, *args, **kwargs):
        kwargs = {**self.retry_kwargs, **kwargs}
        return await rcall(self.function, *args, timing=True, **kwargs)

    async def forward(self):
        await self.worklog.forward()
        await self.worklog.queue.process()

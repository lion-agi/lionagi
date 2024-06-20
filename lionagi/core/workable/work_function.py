"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from lionagi.os.lib import rcall
from lionagi.os.core.work.worklog import WorkLog


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
        """
        Initializes a WorkFunction instance.

        Args:
            assignment (str): The assignment description of the work function.
            function (Callable): The function to be performed.
            retry_kwargs (dict, optional): The retry arguments for the function.
                Defaults to None.
            guidance (str, optional): The guidance or documentation for the function.
                Defaults to None.
            capacity (int, optional): The capacity of the work log. Defaults to 10.
        """
        self.assignment = assignment
        self.function = function
        self.retry_kwargs = retry_kwargs or {}
        self.worklog = WorkLog(capacity)
        self.guidance = guidance or self.function.__doc__

    @property
    def name(self):
        """
        Gets the name of the function.

        Returns:
            str: The name of the function.
        """
        return self.function.__name__

    def is_progressable(self):
        """
        Checks if the work function is progressable.

        Returns:
            bool: True if the work function is progressable, otherwise False.
        """
        return self.worklog.pending_work and not self.worklog.stopped

    async def perform(self, *args, **kwargs):
        """
        Performs the work function with retry logic.

        Args:
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Any: The result of the function call.
        """
        kwargs = {**self.retry_kwargs, **kwargs}
        return await rcall(self.function, *args, timing=True, **kwargs)

    async def forward(self):
        """
        Forwards the work log and processes the work queue.
        """
        await self.worklog.forward()
        await self.worklog.queue.process()

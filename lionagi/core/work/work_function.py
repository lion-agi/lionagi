import asyncio

from lionagi.core.work.worklog import WorkLog
from lionagi.libs.ln_func_call import rcall


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
        self,
        assignment,
        function,
        retry_kwargs=None,
        guidance=None,
        capacity=10,
        refresh_time=1,
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
            capacity (int, optional): The capacity of the work queue batch processing.
                Defaults to 10.
            refresh_time (int, optional): The time interval to refresh the work log queue.
                Defaults to 1.
        """
        self.assignment = assignment
        self.function = function
        self.retry_kwargs = retry_kwargs or {}
        self.worklog = WorkLog(capacity, refresh_time=refresh_time)
        self.guidance = guidance or self.function.__doc__

    @property
    def name(self):
        """
        Gets the name of the function.

        Returns:
            str: The name of the function.
        """
        return self.function.__name__

    @property
    def execution_mode(self):
        """
        Gets the execution mode of the work function's queue.

        Returns:
            bool: The execution mode of the work function's queue.
        """
        return self.worklog.queue.execution_mode

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
        Forward the work log to work queue.
        """
        await self.worklog.forward()

    async def process(self):
        """
        Process the first capacity_size works in the work queue.
        """
        await self.worklog.queue.process()

    async def execute(self):
        """
        Starts the execution of the work function's queue.
        """
        asyncio.create_task(self.worklog.queue.execute())

    async def stop(self):
        """
        Stops the execution of the work function's queue.
        """
        await self.worklog.stop()

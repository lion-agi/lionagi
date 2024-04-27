from lionagi.libs import func_call

from ._logger import WorkLogger


class WorkFunction:
    """
    Represents a functional unit of work that encapsulates the behavior necessary to
    execute a specific function, manage retries, and track execution through a logger.

    Attributes:
        assignment (str): Description or purpose of the work function.
        function (callable): The function to be executed as part of the work.
        retry_kwargs (dict): Additional keyword arguments to handle retries.
        manual (str): Manual or documentation derived from the function or provided explicitly.
        worklog (WorkLogger): Logger to manage and track the state and progress of work.

    Methods:
        perform(*args, **kwargs): Executes the function with specified arguments and retry logic.
        process(refresh_time): Processes logged work items.
        stop(): Stops the work processing.
        clear_count(): Clears the processed count in the work logger.
    """

    def __init__(
        self,
        assignment,
        function,
        retry_kwargs=None,
        manual=None,
        capacity=None,
        refresh_time=None,
    ):
        """
        Initializes a WorkFunction with a specified function, assignment, and logging capabilities.

        Args:
            assignment (str): Description or purpose of the work function.
            function (callable): The function to be executed.
            retry_kwargs (dict, optional): Keyword arguments for retry logic.
            manual (str, optional): Manual or documentation for the function; defaults to the function's docstring.
            capacity (int, optional): The maximum number of concurrent tasks the logger can handle.
            refresh_time (float, optional): Time to wait after a batch of tasks is processed.
        """
        self.assignment = assignment
        self.function = function
        self.retry_kwargs = retry_kwargs if retry_kwargs is not None else {}
        self.manual = manual if manual is not None else function.__doc__
        self.worklog = WorkLogger(capacity=capacity, refresh_time=refresh_time)

    @property
    def name(self):
        """
        Retrieves the name of the function.

        Returns:
            str: The name of the function.
        """
        return self.function.__name__

    async def perform(self, *args, **kwargs):
        """
        Executes the assigned function asynchronously with provided arguments and
        retry mechanisms.

        Args:
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function, merged with retry_kwargs.

        Returns:
            The result of the function execution.
        """
        combined_kwargs = {**self.retry_kwargs, **kwargs}
        return await func_call.rcall(self.function, *args, timing=True, **combined_kwargs)

    async def process(self, refresh_time=None):
        """
        Processes the work items logged in the work logger.

        Args:
            refresh_time (float, optional): Time to pause after a batch of tasks is processed.
        """
        await self.worklog.process(refresh_time)

    async def stop(self):
        """
        Stops the processing of work items in the logger.
        """
        await self.worklog.stop()

    async def clear_count(self):
        """
        Clears the count of processed tasks in the work logger.
        """
        await self.worklog.clear_count()

    @property
    def count(self):
        """
        Retrieves the count of processed tasks from the work logger.

        Returns:
            int: The number of processed tasks.
        """
        return self.worklog.count

    @property
    def completed_work(self):
        """
        Retrieves completed work items from the logger.

        Returns:
            dict: A dictionary of completed work items.
        """
        return self.worklog.completed_work

    def __repr__(self):
        """
        Returns a machine-readable representation of the WorkFunction.

        Returns:
            str: Representation of the WorkFunction.
        """
        return f"<WorkFunction {self.name}>"

    def __str__(self):
        """
        Returns a human-readable description of the WorkFunction.

        Returns:
            str: Description of the WorkFunction including its name and assignment.
        """
        return f"WorkFunction(name={self.name}, assignment={self.assignment}, instruction={self.manual})"

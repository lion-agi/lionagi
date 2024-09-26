import asyncio

from lionagi.core.work.work import WorkStatus


class WorkQueue:
    """
    A class representing a queue for managing work.

    Attributes:
        capacity (int): The maximum number of tasks the queue can handle.
        queue (asyncio.Queue): The queue holding the tasks.
        _stop_event (asyncio.Event): Event to signal stopping the execution of the queue.
        available_capacity (int): The remaining number of tasks the queue can handle.
        execution_mode (bool): If `execute` is running.
        refresh_time (int): The time interval between task processing.
    """

    def __init__(self, capacity=5, refresh_time=1):
        """
        Initializes a new instance of WorkQueue.

        Args:
            capacity (int): The maximum number of tasks the queue can handle.
            refresh_time (int): The time interval between task processing.

        Raises:
            ValueError: If capacity is less than 0 or refresh_time is negative.
        """
        if capacity < 0:
            raise ValueError("initial capacity must be >= 0")
        if refresh_time < 0:
            raise ValueError("refresh time for execution can not be negative")
        self.capacity = capacity
        self.queue = asyncio.Queue()
        self._stop_event = asyncio.Event()
        self.available_capacity = capacity
        self.execution_mode = False
        self.refresh_time = refresh_time

    async def enqueue(self, work) -> None:
        """Enqueue a work item."""
        await self.queue.put(work)

    async def dequeue(self):
        """Dequeue a work item."""
        return await self.queue.get()

    async def join(self) -> None:
        """Block until all items in the queue have been processed."""
        await self.queue.join()

    async def stop(self) -> None:
        """Signal the queue to stop processing."""
        self._stop_event.set()

    @property
    def stopped(self) -> bool:
        """Return whether the queue has been stopped."""
        return self._stop_event.is_set()

    async def process(self) -> None:
        """Process the work items in the queue."""
        tasks = set()
        while self.available_capacity > 0 and self.queue.qsize() > 0:
            next = await self.dequeue()
            next.status = WorkStatus.IN_PROGRESS
            task = asyncio.create_task(next.perform())
            tasks.add(task)
            self.available_capacity -= 1

        if tasks:
            await asyncio.wait(tasks)
            self.available_capacity = self.capacity

    async def execute(self):
        """
        Continuously executes the process method at a specified refresh interval.

        Args:
            refresh_time (int, optional): The time in seconds to wait between
                successive calls to `process`. Defaults to 1.
        """
        self.execution_mode = True
        self._stop_event.clear()

        while not self.stopped:
            await self.process()
            await asyncio.sleep(self.refresh_time)
        self.execution_mode = False

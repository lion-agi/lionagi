import asyncio

class WorkQueue:
    """
    Manages a queue of asynchronous tasks, allowing for concurrent processing with
    a fixed capacity. The class provides methods to enqueue tasks, dequeue tasks,
    wait for all tasks to complete, and to stop processing new tasks.

    Attributes:
        queue (asyncio.Queue): The queue that holds tasks.
        stop_event (asyncio.Event): An event to signal that the queue should stop.
        capacity (int): The maximum number of tasks the queue can hold.
        semaphore (asyncio.Semaphore): Limits the number of tasks processed concurrently.
        processed_count (int): Counts the number of tasks that have been processed.

    Methods:
        enqueue(work): Adds a task to the queue.
        dequeue(): Retrieves a task from the queue.
        join(): Waits until the queue is empty.
        stop(): Signals to stop processing tasks.
        process(): Processes tasks until the queue is stopped or empty.
        clear_processed_count(): Resets the count of processed tasks.
    """

    def __init__(self, capacity=None):
        """
        Initializes the WorkQueue with an optional capacity limit.

        Args:
            capacity (int, optional): The maximum number of concurrent tasks. If None,
                                      the queue will be unbounded.
        """
        self.queue = asyncio.Queue(capacity)
        self.stop_event = asyncio.Event()
        self.capacity = capacity
        self.semaphore = asyncio.Semaphore(capacity if capacity is not None else float('inf'))
        self.processed_count = 0

    async def enqueue(self, work):
        """
        Asynchronously adds a task to the queue.

        Args:
            work: The task to be added. Must be awaitable.
        """
        await self.queue.put(work)

    async def dequeue(self):
        """
        Asynchronously removes and returns a task from the queue.

        Returns:
            Returns the task removed from the queue.
        """
        return await self.queue.get()

    async def join(self):
        """
        Awaits until the queue is empty and all tasks have been processed.
        """
        await self.queue.join()

    async def stop(self):
        """
        Signals the queue to stop processing tasks.
        """
        self.stop_event.set()

    @property
    def available_capacity(self):
        """
        Calculates and returns the remaining capacity of the queue.

        Returns:
            The available capacity of the queue or None if the queue is unbounded.
        """
        if self.capacity is None:
            return None
        return self.capacity - self.queue.qsize()

    @property
    def stopped(self):
        """
        Checks whether the queue has been stopped.

        Returns:
            True if the queue is stopped, False otherwise.
        """
        return self.stop_event.is_set()

    async def process(self):
        """
        Processes tasks from the queue as long as it is not stopped and there are items to process.
        Each task is expected to implement a 'perform' method which is awaited.

        Raises:
            RuntimeError: If an error occurs during task processing.
        """
        tasks = set()
        try:
            while not self.queue.empty() and not self.stopped:
                if self.available_capacity <= 0 and tasks:
                    _, done = await asyncio.wait(
                        tasks, return_when=asyncio.FIRST_COMPLETED)
                    tasks.difference_update(done)

                async with self.semaphore:
                    task = await self.dequeue()
                    if task is None:
                        break
                    task = asyncio.create_task(task.perform())
                    tasks.add(task)

                if tasks:
                    await asyncio.wait(tasks)
                    self.processed_count += len(tasks)
        except Exception as exc:
            raise RuntimeError(f"Error during task processing: {exc}")

    async def clear_processed_count(self):
        """
        Resets the processed task counter to zero.
        """
        self.processed_count = 0

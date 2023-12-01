import asyncio
from typing import Callable, Any

class AsyncQueue:
    """A queue class that handles asynchronous operations.

    Attributes:
        queue: An asyncio Queue to hold the items.
        _stop_event: An asyncio Event to signal when to stop the queue processing.

    Methods:
        enqueue: Add an item to the queue.
        dequeue: Remove and return an item from the queue.
        join: Block until all items in the queue have been processed and marked as done.
        stop: Signal the queue to stop processing.
        stopped: Check if the queue is signaled to stop.
        process_requests: Process items from the queue using the provided function.
    """
    
    def __init__(self):
        """Initialize an AsyncQueue with an asyncio Queue and stop event."""
        self.queue = asyncio.Queue()
        self._stop_event = asyncio.Event()

    async def enqueue(self, item):
        """Add an item to the queue.
        
        Args:
            item: The item to be added to the queue.
        """
        await self.queue.put(item)

    async def dequeue(self) -> Any:
        """Remove and return an item from the queue."""
        return await self.queue.get()

    async def join(self) -> None:
        """Block until all items in the queue have been processed and marked as done."""
        await self.queue.join()

    async def stop(self) -> None:
        """Signal the queue to stop processing."""
        self._stop_event.set()

    def stopped(self) -> bool:
        """Check if the queue is signaled to stop.

        Returns:
            True if the queue is signaled to stop, False otherwise.
        """
        return self._stop_event.is_set()

    async def process_requests(self, func: Callable[[Any], Any]) -> None:
        """Process items from the queue using the provided function.

        Args:
            func: A coroutine function that processes items from the queue.
        """
        while not self.stopped():
            item = await self.dequeue()
            if item is None:  # Using `None` as a sentinel value to cease processing.
                self._stop_event.set()
                break
            await func(item)
            
import asyncio
from collections import deque

from .._status import WorkStatus
from ._queue import WorkQueue
from ._work import Work


class WorkLogger:
    """
    Manages logging and processing of work items using an asynchronous queue system.
    The logger handles tasks, maintaining a sequence of pending work items and a dictionary
    of tasks that allows tracking their status.

    Attributes:
        pile (dict): Maps work item IDs to work items, storing their current status and data.
        pending_sequence (deque): A sequence of IDs representing work items pending processing.
        queue (WorkQueue): An asynchronous queue that manages the execution of work items.
        refresh_time (float, optional): The time interval to wait after processing tasks.
        add_count (int): A counter tracking the number of work items added.

    Methods:
        append(work): Adds a work item to the logger and prepares it for processing.
        forward(): Moves work from pending to the queue if there is available capacity.
        process(refresh_time): Processes work items from the queue continuously.
        stop(): Signals the queue to stop processing work items.
    """

    def __init__(self, capacity=None, pile=None, refresh_time=None):
        """
        Initializes a WorkLogger with a specified capacity for the work queue.

        Args:
            capacity (int, optional): The maximum number of concurrent tasks the queue can handle.
            pile (dict, optional): Initial dictionary of work items.
            refresh_time (float, optional): The time to pause after a batch of tasks is processed.
        """
        self.pile = pile if pile is not None else {}
        self.pending_sequence = deque()
        self.queue = WorkQueue(capacity=capacity)
        self.refresh_time = refresh_time
        self.add_count = 0

    async def append(self, work: Work):
        """
        Adds a work item to the logger's tracking system and schedules it for processing.

        Args:
            work (Work): The work item to be added.
        """
        self.pile[work.id_] = work
        self.pending_sequence.append(work.id_)
        self.add_count += 1

    async def forward(self):
        """
        Transfers work items from the pending sequence to the processing queue if there is
        available capacity in the queue.

        Returns:
            bool: False indicating the forward operation has completed (whether successful or not).
        """
        if not self.queue.available_capacity:
            return False
        while self.pending_sequence and self.queue.available_capacity:
            work_id = self.pending_sequence.popleft()
            work = self.pile[work_id]
            work.status = WorkStatus.IN_PROGRESS
            await self.queue.enqueue(work)
        return True

    async def process(self, refresh_time=None):
        """
        Continuously processes work items, forwarding them from the pending sequence to the queue
        and then initiating their processing, with pauses determined by the refresh time.

        Args:
            refresh_time (float, optional): Optional override for the default refresh time.
        """
        while self.pending_sequence and not self.queue.is_stopped:
            if await self.forward():
                await self.queue.process()
                await asyncio.sleep(refresh_time or self.refresh_time)

    async def stop(self):
        """
        Signals the queue to stop processing new work items.
        """
        await self.queue.stop()

    @property
    def stopped(self):
        """
        Checks if the work queue has been stopped.

        Returns:
            bool: True if the queue is stopped, otherwise False.
        """
        return self.queue.is_stopped

    @property
    def completed_work(self):
        """
        Retrieves a dictionary of completed work items.

        Returns:
            dict: A dictionary mapping work item IDs to completed work items.
        """
        return {id_: work for id_, work in self.pile.items() if work.status == WorkStatus.COMPLETED}

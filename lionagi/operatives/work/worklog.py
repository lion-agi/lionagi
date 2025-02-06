from lionagi.protocols._concepts import Ordering
from lionagi.protocols.generic.element import Element
from lionagi.protocols.generic.event import EventStatus
from lionagi.protocols.generic.log import Log
from lionagi.protocols.generic.pile import Pile, pile
from lionagi.protocols.generic.progression import Progression, prog
from lionagi.utils import to_dict

from .work import Work
from .work_queue import WorkQueue


class WorkLog(Element, Ordering[Work]):
    """
    A class representing a log of work items.

    This class extends Element to provide unique identification and timestamp tracking,
    while implementing Ordering to manage the sequence of work items.

    Attributes:
        pile (Pile[Work]): A pile containing work items.
        pending (Progression[Work]): A progression of pending work items.
        queue (WorkQueue): A queue to manage the execution of work items.
    """

    def __init__(
        self,
        capacity: int = 10,
        workpile: Pile[Work] | None = None,
        refresh_time: float = 1,
    ):
        """
        Initializes a new instance of WorkLog.

        Args:
            capacity (int): The capacity of the work queue batch processing.
            workpile (Pile[Work], optional): An optional pile of initial work items.
            refresh_time (float): The time interval to refresh the work log queue.
                Defaults to 1.
        """
        super().__init__()
        self.pile = (
            workpile
            if workpile and isinstance(workpile, Pile)
            else pile(item_type=Work)
        )
        self.pending = prog(workpile) if workpile else Progression()
        self.queue = WorkQueue(capacity=capacity, refresh_time=refresh_time)

    async def append(self, work: Work) -> None:
        """
        Appends a new work item to the log.

        Args:
            work (Work): The work item to append.
        """
        self.pile.include(work)
        self.pending.include(work)

    async def forward(self) -> None:
        """
        Forwards pending work items to the queue.
        """
        while len(self.pending) > 0:
            work: Work = self.pile[self.pending.popleft()]
            await self.queue.enqueue(work)

    async def stop(self) -> None:
        """
        Stops the work queue.
        """
        await self.queue.stop()

    def include(self, item: Work, /) -> None:
        """
        Include a work item in the log.

        Args:
            item (Work): The work item to include.
        """
        self.pile.include(item)
        self.pending.include(item)

    def exclude(self, item: Work, /) -> None:
        """
        Exclude a work item from the log.

        Args:
            item (Work): The work item to exclude.
        """
        self.pile.exclude(item)
        self.pending.exclude(item)

    @property
    def pending_work(self) -> Pile[Work]:
        """
        Retrieves the pile of pending work items.

        Returns:
            Pile[Work]: A pile of pending work items.
        """
        return pile(
            [i for i in self.pile if i.status == EventStatus.PENDING],
            item_type=Work,
        )

    @property
    def stopped(self) -> bool:
        """
        Checks if the work queue is stopped.

        Returns:
            bool: True if the work queue is stopped, else False.
        """
        return self.queue.stopped

    @property
    def completed_work(self) -> Pile[Work]:
        """
        Retrieves the pile of completed work items.

        Returns:
            Pile[Work]: A pile of completed work items.
        """
        return pile(
            [i for i in self.pile if i.status == EventStatus.COMPLETED],
            item_type=Work,
        )

    def to_log(self) -> Log:
        """Create a Log object summarizing this worklog."""
        return Log(
            content={
                "type": "WorkLog",
                "id": str(self.id),
                "pending_count": len(self.pending_work),
                "completed_count": len(self.completed_work),
                "total_count": len(self.pile),
                "queue_status": {
                    "capacity": self.queue.queue_capacity,
                    "available": self.queue.available_capacity,
                    "execution_mode": self.queue.execution_mode,
                    "stopped": self.queue.stopped,
                },
                "works": [
                    {
                        "id": str(w.id),
                        "status": str(w.status),
                        "task_name": w.async_task_name,
                        "response": to_dict(w.execution.response),
                        "error": w.execution.error,
                    }
                    for w in self.pile
                ],
            }
        )

    def __contains__(self, work: Work) -> bool:
        """
        Checks if a work item is in the pile.

        Args:
            work (Work): The work item to check.

        Returns:
            bool: True if the work item is in the pile, else False.
        """
        return work in self.pile

    def __iter__(self):
        """
        Returns an iterator over the work pile.

        Returns:
            Iterator: An iterator over the work pile.
        """
        return iter(self.pile)

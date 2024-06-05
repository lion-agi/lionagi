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

from lionagi.os.collections.abc import Progressable
from lionagi.os.collections import pile, progression, Pile
from lionagi.os.core.work.work import Work, WorkStatus
from lionagi.os.core.work.work_queue import WorkQueue


class WorkLog(Progressable):
    """
    A class representing a log of work items.

    Attributes:
        pile (Pile): A pile containing work items.
        pending (Progression): A progression of pending work items.
        queue (WorkQueue): A queue to manage the execution of work items.
    """

    def __init__(self, capacity=10, workpile=None):
        """
        Initializes a new instance of WorkLog.

        Args:
            capacity (int): The capacity of the work queue.
            workpile (Pile, optional): An optional pile of initial work items.
        """
        self.pile = (
            workpile if workpile and isinstance(workpile, Pile) else pile({}, Work)
        )
        self.pending = progression(workpile) if workpile else progression()
        self.queue = WorkQueue(capacity=capacity)

    async def append(self, work: Work):
        """
        Appends a new work item to the log.

        Args:
            work (Work): The work item to append.
        """
        self.pile.append(work)
        self.pending.append(work)

    async def forward(self):
        """
        Forwards pending work items to the queue if capacity allows.
        """
        if not self.queue.available_capacity:
            return
        else:
            while len(self.pending) > 0 and self.queue.available_capacity:
                work: Work = self.pile[self.pending.popleft()]
                work.status = WorkStatus.IN_PROGRESS
                await self.queue.enqueue(work)

    async def stop(self):
        """
        Stops the work queue.
        """
        await self.queue.stop()

    @property
    def pending_work(self):
        """
        Retrieves the pile of pending work items.

        Returns:
            Pile: A pile of pending work items.
        """
        return pile([i for i in self.pile if i.status == WorkStatus.PENDING])

    @property
    def stopped(self):
        """
        Checks if the work queue is stopped.

        Returns:
            bool: True if the work queue is stopped, else False.
        """
        return self.queue.stopped

    @property
    def completed_work(self):
        """
        Retrieves the pile of completed work items.

        Returns:
            Pile: A pile of completed work items.
        """
        return pile([i for i in self.pile if i.status == WorkStatus.COMPLETED])

    def __contains__(self, work):
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

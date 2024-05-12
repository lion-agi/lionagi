from ..generic.abc import Progressable
from ..generic import pile, progression, Pile

from .work import Work, WorkStatus
from .work_queue import WorkQueue


class WorkLog(Progressable):

    def __init__(self, capacity=10, workpile=None):
        self.pile = (
            workpile if workpile and isinstance(workpile, Pile) else pile({}, Work)
        )
        self.pending = progression(workpile) if workpile else progression()
        self.queue = WorkQueue(capacity=capacity)

    async def append(self, work: Work):
        self.pile.append(work)
        self.pending.append(work)

    async def forward(self):
        if not self.queue.available_capacity:
            return
        else:
            while len(self.pending) > 0 and self.queue.available_capacity:
                work: Work = self.pile[self.pending.popleft()]
                work.status = WorkStatus.IN_PROGRESS
                await self.queue.enqueue(work)

    async def stop(self):
        await self.queue.stop()

    @property
    def pending_work(self):
        return pile([i for i in self.pile if i.status == WorkStatus.PENDING])

    @property
    def stopped(self):
        return self.queue.stopped

    @property
    def completed_work(self):
        return pile([i for i in self.pile if i.status == WorkStatus.COMPLETED])

    def __contains__(self, work):
        return work in self.pile

    def __iter__(self):
        return iter(self.pile)

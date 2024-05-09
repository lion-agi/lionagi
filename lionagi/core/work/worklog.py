from ..generic.abc import Progressable
from ..generic import pile, progression, Pile

from .schema import Work, WorkStatus
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
    def stopped(self):
        return self.queue.stopped

    @property
    def completed_work(self):
        return {k: v for k, v in self.pile.items() if v.status == WorkStatus.COMPLETED}

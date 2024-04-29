import asyncio


class WorkQueue:

    def __init__(self, capacity=5):

        self.queue = asyncio.Queue()
        self._stop_event = asyncio.Event()
        self.capacity = capacity
        self.semaphore = asyncio.Semaphore(capacity)

    async def enqueue(self, work) -> None:
        await self.queue.put(work)

    async def dequeue(self):
        return await self.queue.get()

    async def join(self) -> None:
        await self.queue.join()

    async def stop(self) -> None:
        self._stop_event.set()

    @property
    def available_capacity(self):
        if (a:= self.capacity - self.queue.qsize()) > 0:
            return a    
        return None
    
    @property
    def stopped(self) -> bool:
        return self._stop_event.is_set()


    async def process(self, refresh_time=1) -> None:
        tasks = set()
        while self.queue.qsize() > 0 and not self.stopped:
            if not self.available_capacity and tasks:
                _, done = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                tasks.difference_update(done)

            async with self.semaphore:
                next = await self.dequeue()
                if next is None:
                    break
                task = asyncio.create_task(next.perform())
                tasks.add(task)

            if tasks:
                await asyncio.wait(tasks)
        await asyncio.sleep(refresh_time)



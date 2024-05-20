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

import asyncio


class WorkQueue:
    """
    A class representing a queue for managing work.

    Attributes:
        capacity (int): The maximum number of tasks the queue can handle.
        queue (asyncio.Queue): The queue holding the tasks.
        _stop_event (asyncio.Event): Event to signal stopping of the queue.
        semaphore (asyncio.Semaphore): Semaphore to control access based on capacity.
    """

    def __init__(self, capacity=5):

        self.queue = asyncio.Queue()
        self._stop_event = asyncio.Event()
        self.capacity = capacity
        self.semaphore = asyncio.Semaphore(capacity)

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
    def available_capacity(self):
        """Return the available capacity of the queue."""
        available = self.capacity - self.queue.qsize()
        return available if available > 0 else None

    @property
    def stopped(self) -> bool:
        """Return whether the queue has been stopped."""
        return self._stop_event.is_set()

    async def process(self) -> None:
        """Process the work items in the queue."""
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

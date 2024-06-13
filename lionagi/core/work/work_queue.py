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
from lionagi.core.work.work import WorkStatus


class WorkQueue:
    """
    A class representing a queue for managing work.

    Attributes:
        capacity (int): The maximum number of tasks the queue can handle.
        queue (asyncio.Queue): The queue holding the tasks.
        _stop_event (asyncio.Event): Event to signal stopping `execute` of the queue.
        available_capacity (int): The remaining number of tasks the queue can handle.
        execution_mode (bool): If `execute` is running.
    """

    def __init__(self, capacity=5):
        if capacity < 0:
            raise ValueError("initial capacity must be >= 0")
        self.capacity = capacity
        self.queue = asyncio.Queue()
        self._stop_event = asyncio.Event()
        self.available_capacity = capacity
        self.execution_mode = False

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

    # async def process(self):
        # async def _parse_work(work):
        #     async with self.semaphore:
        #         await work.perform()
        #
        # tasks = set()
        # while self.queue.qsize() > 0:
        #     next = await self.dequeue()
        #     next.status = WorkStatus.IN_PROGRESS
        #     task = asyncio.create_task(_parse_work(next))
        #     tasks.add(task)
        #
        # await asyncio.wait(tasks)

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

    async def execute(self, refresh_time=1):
        """
            Continuously executes the process method at a specified refresh interval.

            Args:
                refresh_time (int, optional): The time in seconds to wait between
                    successive calls to `process`. Defaults to 1.
        """
        self.execution_mode = True
        while not self.stopped:
            await self.process()
            await asyncio.sleep(refresh_time)
        self.execution_mode = False

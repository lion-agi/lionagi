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
from typing import ClassVar

from lionagi.protocols.generic.event import EventStatus
from lionagi.protocols.generic.processor import Processor

from .work import Work


class WorkQueue(Processor):
    """
    A queue for managing and processing work items.

    This class extends Processor to provide specialized handling of Work items,
    with support for capacity management, async processing, and status tracking.

    Attributes:
        event_type (ClassVar[type[Work]]): The type of events this queue processes.
        queue_capacity (int): The maximum number of tasks the queue can handle.
        capacity_refresh_time (float): The time interval between task processing.
        _available_capacity (int): The remaining number of tasks the queue can handle.
        _execution_mode (bool): If `execute` is running.
        _stop_event (asyncio.Event): Event to signal stopping the execution.
    """

    event_type: ClassVar[type[Work]] = Work

    def __init__(self, capacity: int = 5, refresh_time: float = 1):
        """
        Initializes a new instance of WorkQueue.

        Args:
            capacity (int): The maximum number of tasks the queue can handle.
            refresh_time (float): The time interval between task processing.

        Raises:
            ValueError: If capacity is less than 0 or refresh_time is negative.
        """
        if capacity < 0:
            raise ValueError("initial capacity must be >= 0")
        if refresh_time < 0:
            raise ValueError("refresh time for execution can not be negative")

        super().__init__(
            queue_capacity=capacity,
            capacity_refresh_time=refresh_time,
            concurrency_limit=None,
        )

    async def process(self) -> None:
        """Process work items in the queue up to the available capacity."""
        tasks = set()
        while self.available_capacity > 0 and not self.queue.empty():
            next_work = await self.dequeue()
            next_work.status = EventStatus.PROCESSING
            task = asyncio.create_task(next_work.invoke())
            tasks.add(task)
            self.available_capacity -= 1

        if tasks:
            await asyncio.wait(tasks)
            self.available_capacity = self.queue_capacity

    async def execute(self):
        """
        Continuously executes the process method at a specified refresh interval.
        """
        self.execution_mode = True
        await self.start()

        while not self.is_stopped():
            await self.process()
            await asyncio.sleep(self.capacity_refresh_time)

        self.execution_mode = False

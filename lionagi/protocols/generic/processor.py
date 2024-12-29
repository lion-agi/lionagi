# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from typing import Any, ClassVar

from lionagi.utils import DataClass

from .concepts import Observer
from .element import ID
from .event import Event, EventStatus
from .pile import Pile, Progression

__all__ = (
    "Processor",
    "Executor",
)


class Processor(Observer):
    """should subclass to really use this"""

    event_type: ClassVar[type[Event]]

    def __init__(
        self,
        queue_capacity: int,
        capacity_refresh_time: float,
    ):
        super().__init__()
        if queue_capacity < 1:
            raise ValueError("Queue capacity must be greater than 0.")
        if capacity_refresh_time <= 0:
            raise ValueError("Capacity refresh time must be larger than 0.")

        self.queue_capacity = queue_capacity
        self.capacity_refresh_time = capacity_refresh_time
        self.queue = asyncio.Queue()
        self._available_capacity = queue_capacity
        self._execution_mode = False
        self._stop_event = asyncio.Event()

    @property
    def available_capacity(self) -> int:
        return self._available_capacity

    @available_capacity.setter
    def available_capacity(self, value: int) -> None:
        self._available_capacity = value

    @property
    def execution_mode(self) -> bool:
        return self._execution_mode

    @execution_mode.setter
    def execution_mode(self, value: bool) -> None:
        self._execution_mode = value

    async def enqueue(self, event: Event) -> None:
        """
        Enqueues an event to the processor queue.

        Args:
            event: The event to be added to the queue.
        """
        await self.queue.put(item=event)

    async def dequeue(self) -> Event:
        """
        Dequeues an event from the processor queue.

        Returns:
            The next event in the queue.
        """
        return await self.queue.get()

    async def join(self) -> None:
        """Blocks until all items in the queue have been processed."""
        await self.queue.join()

    async def stop(self) -> None:
        """Signals the processor to stop processing actions."""
        self._stop_event.set()

    async def start(self) -> None:
        """Allows the processor to start or continue processing."""
        self._stop_event.clear()

    def is_stopped(self) -> bool:
        """
        Indicates whether the processor has been stopped.

        Returns:
            True if the processor has been stopped, otherwise False.
        """
        return self._stop_event.is_set()

    @classmethod
    async def create(cls, **kwargs: Any) -> "Processor":
        """
        Class method to create an instance of the processor.

        Args:
            **kwargs: Arguments passed to the processor constructor.

        Returns:
            A new instance of the processor.
        """
        processor = cls(**kwargs)
        return processor

    async def process(self) -> None:
        """
        Processes the work items in the queue.

        Processes items up to the available capacity. Each action is marked as
        `PROCESSING` before execution. After processing, capacity is reset.
        """
        tasks = set()
        prev, next = None, None

        while self.available_capacity > 0 and self.queue.qsize() > 0:
            if prev and prev.status == EventStatus.PENDING:
                next = prev
                await asyncio.sleep(self.capacity_refresh_time)
            else:
                next: Event = await self.dequeue()

            if await self.request_permission(**next.request):
                next.status = EventStatus.PROCESSING
                task = asyncio.create_task(next.invoke())
                tasks.add(task)
            prev = next

        if tasks:
            await asyncio.wait(tasks)
            self.available_capacity = self.queue_capacity

    async def request_permission(self, **kwargs: Any) -> bool:
        return True

    async def execute(self) -> None:
        """
        Executes the processor, continuously processing actions until stopped.

        Runs in a loop, processing actions and respecting the refresh time
        between cycles. Exits when signaled to stop.
        """
        self._execution_mode = True
        await self.start()

        while not self.is_stopped():
            await self.process()
            await asyncio.sleep(self.capacity_refresh_time)
        self._execution_mode = False


class Executor(DataClass, Observer):
    """should subclass to really use this"""

    processor_type: ClassVar[type[Processor]]

    def __init__(
        self,
        processor_config: dict[str, Any] = None,
        strict_event_type: bool = False,
    ):
        self.processor_config = processor_config or {}
        self.pending = Progression()
        self.processor = None
        self.pile: Pile[Event] = Pile(
            item_type=self.processor_type.event_type,
            strict_type=strict_event_type,
        )

    @property
    def event_type(self) -> type[Event]:
        return self.processor_type.event_type

    @property
    def strict_event_type(self) -> bool:
        return self.pile.strict_type

    async def forward(self) -> None:
        """Forwards pending actions to the processor."""
        while len(self.pending) > 0:
            action = self.pile[self.pending.popleft()]
            await self.processor.enqueue(action)
        await self.processor.process()

    async def start(self) -> None:
        """Starts the event processor."""
        if not self.processor:
            await self._create_processor()
        await self.processor.start()

    async def stop(self) -> None:
        """Stops the event processor."""
        if self.processor:
            await self.processor.stop()

    async def _create_processor(self) -> None:
        """Factory method the processor creation"""
        self.processor = await self.processor_type.create(
            **self.processor_config,
        )

    async def append(self, event: Event) -> None:
        """
        Appends a new action to the executor.

        Args:
            action (ObservableAction): The action to be added to the pile.
        """
        async with self.pile:
            self.pile.include(event)
            self.pending.include(event)

    @property
    def completed_events(self) -> Pile[Event]:
        """
        Retrieves a pile of all completed actions.

        Returns:
            Pile: A collection of actions that have been completed.
        """
        return Pile(
            collections=[
                i for i in self.pile if i.status == EventStatus.COMPLETED
            ],
            item_type=self.processor_type.event_type,
            strict_type=self.strict_event_type,
        )

    @property
    def pending_events(self) -> Pile[Event]:
        """
        Retrieves a pile of all pending actions.

        Returns:
            Pile: A collection of actions that are still pending.
        """
        return Pile(
            collections=[
                i for i in self.pile if i.status == EventStatus.PENDING
            ],
            item_type=self.processor_type.event_type,
            strict_type=self.strict_event_type,
        )

    @property
    def failed_events(self) -> Pile[Event]:
        """
        Retrieves a pile of all failed actions.

        Returns:
            Pile: A collection of actions that have failed.
        """
        return Pile(
            collections=[
                i for i in self.pile if i.status == EventStatus.FAILED
            ],
            item_type=self.processor_type.event_type,
            strict_type=self.strict_event_type,
        )

    def __contains__(self, event: ID[Event].Ref) -> bool:
        """Checks if an action is present in the pile."""
        return event in self.pile

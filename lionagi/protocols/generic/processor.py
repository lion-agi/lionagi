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
    """Should subclass to really use this.

    This class manages a queue of events and processes them up to a specified
    capacity within a configured refresh time. Users should subclass this
    class to provide custom logic for how events are processed or how
    permissions are requested.
    """

    event_type: ClassVar[type[Event]]

    def __init__(
        self,
        queue_capacity: int,
        capacity_refresh_time: float,
    ):
        """Initialize the processor.

        Args:
            queue_capacity (int):
                The maximum number of events that can be processed in
                one batch.
            capacity_refresh_time (float):
                The time interval (in seconds) after which the processor
                capacity is reset.
        """
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
        """int: The current available processing capacity."""
        return self._available_capacity

    @available_capacity.setter
    def available_capacity(self, value: int) -> None:
        self._available_capacity = value

    @property
    def execution_mode(self) -> bool:
        """bool: Indicates whether the processor is in execution mode."""
        return self._execution_mode

    @execution_mode.setter
    def execution_mode(self, value: bool) -> None:
        self._execution_mode = value

    async def enqueue(self, event: Event) -> None:
        """Enqueue an event to the processor queue.

        Args:
            event (Event):
                The event to be added to the queue.
        """
        await self.queue.put(item=event)

    async def dequeue(self) -> Event:
        """Dequeue the next event from the processor queue.

        Returns:
            Event: The next event in the queue.
        """
        return await self.queue.get()

    async def join(self) -> None:
        """Block until all items in the queue have been processed."""
        await self.queue.join()

    async def stop(self) -> None:
        """Signal the processor to stop processing actions."""
        self._stop_event.set()

    async def start(self) -> None:
        """Allow the processor to start or continue processing."""
        self._stop_event.clear()

    def is_stopped(self) -> bool:
        """Check if the processor has been stopped.

        Returns:
            bool: True if the processor has been signaled to stop, False
            otherwise.
        """
        return self._stop_event.is_set()

    @classmethod
    async def create(cls, **kwargs: Any) -> "Processor":
        """Create a new instance of the processor.

        Args:
            **kwargs: Arguments passed to the processor constructor.

        Returns:
            Processor: A new instance of the processor.
        """
        processor = cls(**kwargs)
        return processor

    async def process(self) -> None:
        """Process the queued events up to the available capacity.

        Events are marked as `PROCESSING` before being invoked. After
        processing, the available capacity is reset to the original
        queue capacity.
        """
        tasks = set()
        prev, next_event = None, None

        while self.available_capacity > 0 and self.queue.qsize() > 0:
            if prev and prev.status == EventStatus.PENDING:
                next_event = prev
                await asyncio.sleep(self.capacity_refresh_time)
            else:
                next_event = await self.dequeue()

            if await self.request_permission(**next_event.request):
                next_event.status = EventStatus.PROCESSING
                task = asyncio.create_task(next_event.invoke())
                tasks.add(task)
            prev = next_event

        if tasks:
            await asyncio.wait(tasks)
            self.available_capacity = self.queue_capacity

    async def request_permission(self, **kwargs: Any) -> bool:
        """Request permission to process the event.

        Subclasses can override this method to implement custom logic.

        Args:
            **kwargs (Any):
                Additional parameters for permission logic.

        Returns:
            bool: True if permission is granted, False otherwise.
        """
        return True

    async def execute(self) -> None:
        """Continuously process events until stopped.

        This method runs in a loop, respecting the refresh time between cycles.
        It exits the loop when the processor is signaled to stop.
        """
        self._execution_mode = True
        await self.start()

        while not self.is_stopped():
            await self.process()
            await asyncio.sleep(self.capacity_refresh_time)
        self._execution_mode = False


class Executor(DataClass, Observer):
    """Should subclass to really use this.

    An executor that manages events through a processor, holding them in a
    `Pile` until they can be forwarded for processing.
    """

    processor_type: ClassVar[type[Processor]]

    def __init__(
        self,
        processor_config: dict[str, Any] = None,
        strict_event_type: bool = False,
    ):
        """Initialize the Executor.

        Args:
            processor_config (dict[str, Any] | None):
                Configuration dictionary passed to the processor upon
                creation.
            strict_event_type (bool, optional):
                Whether to strictly enforce the event type constraint in
                the pile.
        """
        self.processor_config = processor_config or {}
        self.pending = Progression()
        self.processor = None
        self.pile: Pile[Event] = Pile(
            item_type=self.processor_type.event_type,
            strict_type=strict_event_type,
        )

    @property
    def event_type(self) -> type[Event]:
        """type[Event]: The event type handled by the processor."""
        return self.processor_type.event_type

    @property
    def strict_event_type(self) -> bool:
        """bool: Whether the pile enforces strict event type constraints."""
        return self.pile.strict_type

    async def forward(self) -> None:
        """Forward all pending events to the processor."""
        while len(self.pending) > 0:
            action = self.pile[self.pending.popleft()]
            await self.processor.enqueue(action)
        await self.processor.process()

    async def start(self) -> None:
        """Start the event processor."""
        if not self.processor:
            await self._create_processor()
        await self.processor.start()

    async def stop(self) -> None:
        """Stop the event processor."""
        if self.processor:
            await self.processor.stop()

    async def _create_processor(self) -> None:
        """Create the processor using the configured processor type."""
        self.processor = await self.processor_type.create(
            **self.processor_config
        )

    async def append(self, event: Event) -> None:
        """Append a new event to the executor.

        Args:
            event (Event):
                The event to be added to the pile and marked as pending.
        """
        async with self.pile:
            self.pile.include(event)
            self.pending.include(event)

    @property
    def completed_events(self) -> Pile[Event]:
        """Pile[Event]: A pile of all completed events."""
        return Pile(
            collections=[
                i for i in self.pile if i.status == EventStatus.COMPLETED
            ],
            item_type=self.processor_type.event_type,
            strict_type=self.strict_event_type,
        )

    @property
    def pending_events(self) -> Pile[Event]:
        """Pile[Event]: A pile of all pending events."""
        return Pile(
            collections=[
                i for i in self.pile if i.status == EventStatus.PENDING
            ],
            item_type=self.processor_type.event_type,
            strict_type=self.strict_event_type,
        )

    @property
    def failed_events(self) -> Pile[Event]:
        """Pile[Event]: A pile of all failed events."""
        return Pile(
            collections=[
                i for i in self.pile if i.status == EventStatus.FAILED
            ],
            item_type=self.processor_type.event_type,
            strict_type=self.strict_event_type,
        )

    def __contains__(self, event: ID[Event].Ref) -> bool:
        """Check if the event is present in the pile.

        Args:
            event (ID[Event].Ref):
                A reference to an event.

        Returns:
            bool: True if the event is in the pile, False otherwise.
        """
        return event in self.pile

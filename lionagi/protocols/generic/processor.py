# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from typing import Any, ClassVar

from .._concepts import Observer
from .element import ID
from .event import Event, EventStatus
from .pile import Pile
from .progression import Progression

__all__ = (
    "Processor",
    "Executor",
)


class Processor(Observer):
    """Manages a queue of events with capacity-limited, async processing.

    Subclass this to provide custom event handling logic or permission
    checks. The processor can enqueue events, handle them in batches, and
    respect a capacity limit that is refreshed periodically.
    """

    event_type: ClassVar[type[Event]]

    def __init__(
        self,
        queue_capacity: int,
        capacity_refresh_time: float,
    ) -> None:
        """Initializes a Processor instance.

        Args:
            queue_capacity (int):
                The maximum number of events processed in one batch.
            capacity_refresh_time (float):
                The time in seconds after which processing capacity is reset.

        Raises:
            ValueError: If `queue_capacity` < 1, or
                `capacity_refresh_time` <= 0.
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
        """int: The current capacity available for processing."""
        return self._available_capacity

    @available_capacity.setter
    def available_capacity(self, value: int) -> None:
        self._available_capacity = value

    @property
    def execution_mode(self) -> bool:
        """bool: Indicates if the processor is actively executing events."""
        return self._execution_mode

    @execution_mode.setter
    def execution_mode(self, value: bool) -> None:
        self._execution_mode = value

    async def enqueue(self, event: Event) -> None:
        """Adds an event to the queue asynchronously.

        Args:
            event (Event): The event to enqueue.
        """
        await self.queue.put(event)

    async def dequeue(self) -> Event:
        """Retrieves the next event from the queue.

        Returns:
            Event: The next event in the queue.
        """
        return await self.queue.get()

    async def join(self) -> None:
        """Blocks until the queue is empty and all tasks are done."""
        await self.queue.join()

    async def stop(self) -> None:
        """Signals the processor to stop processing events."""
        self._stop_event.set()

    async def start(self) -> None:
        """Clears the stop signal, allowing event processing to resume."""
        self._stop_event.clear()

    def is_stopped(self) -> bool:
        """Checks whether the processor is in a stopped state.

        Returns:
            bool: True if the processor has been signaled to stop.
        """
        return self._stop_event.is_set()

    @classmethod
    async def create(cls, **kwargs: Any) -> "Processor":
        """Asynchronously constructs a new Processor instance.

        Args:
            **kwargs:
                Additional initialization arguments passed to the constructor.

        Returns:
            Processor: A newly instantiated processor.
        """
        return cls(**kwargs)

    async def process(self) -> None:
        """Dequeues and processes events up to the available capacity.

        Marks events as PROCESSING, invokes them asynchronously, and waits
        for tasks to complete. Resets capacity afterward if any events
        were processed.
        """
        tasks = set()
        prev_event: Event | None = None

        while self.available_capacity > 0 and not self.queue.empty():
            next_event = None
            if prev_event and prev_event.status == EventStatus.PENDING:
                # Wait if previous event is still pending
                await asyncio.sleep(self.capacity_refresh_time)
                next_event = prev_event
            else:
                next_event = await self.dequeue()

            if await self.request_permission(**next_event.request):
                next_event.status = EventStatus.PROCESSING
                task = asyncio.create_task(next_event.invoke())
                tasks.add(task)

            prev_event = next_event
            self._available_capacity -= 1

        if tasks:
            await asyncio.wait(tasks)
            self.available_capacity = self.queue_capacity

    async def request_permission(self, **kwargs: Any) -> bool:
        """Determines if an event may proceed.

        Override this method for custom checks (e.g., rate limits, user
        permissions).

        Args:
            **kwargs: Additional request parameters.

        Returns:
            bool: True if the event is allowed, False otherwise.
        """
        return True

    async def execute(self) -> None:
        """Continuously processes events until `stop()` is called.

        Respects the capacity refresh time between processing cycles.
        """
        self.execution_mode = True
        await self.start()

        while not self.is_stopped():
            await self.process()
            await asyncio.sleep(self.capacity_refresh_time)

        self.execution_mode = False


class Executor(Observer):
    """Manages events via a Processor and stores them in a `Pile`.

    Subclass this to customize how events are forwarded or tracked.
    Typically, you configure an internal Processor, then add events to
    the Pile, which eventually are passed along to the Processor for
    execution.
    """

    processor_type: ClassVar[type[Processor]]

    def __init__(
        self,
        processor_config: dict[str, Any] | None = None,
        strict_event_type: bool = False,
    ) -> None:
        """Initializes the Executor.

        Args:
            processor_config (dict[str, Any] | None):
                Configuration parameters for creating the Processor.
            strict_event_type (bool):
                If True, the underlying Pile enforces exact type matching
                for Event objects.
        """
        self.processor_config = processor_config or {}
        self.pending = Progression()
        self.processor: Processor | None = None
        self.pile: Pile[Event] = Pile(
            item_type=self.processor_type.event_type,
            strict_type=strict_event_type,
        )

    @property
    def event_type(self) -> type[Event]:
        """type[Event]: The Event subclass handled by the processor."""
        return self.processor_type.event_type

    @property
    def strict_event_type(self) -> bool:
        """bool: Indicates if the Pile enforces exact event type matching."""
        return self.pile.strict_type

    async def forward(self) -> None:
        """Forwards all pending events from the pile to the processor.

        After all events are enqueued, it calls `processor.process()` for
        immediate handling.
        """
        while len(self.pending) > 0:
            id_ = self.pending.popleft()
            event = self.pile[id_]
            await self.processor.enqueue(event)

        await self.processor.process()

    async def start(self) -> None:
        """Initializes and starts the processor if it has not been created."""
        if not self.processor:
            await self._create_processor()
        await self.processor.start()

    async def stop(self) -> None:
        """Stops the processor if it exists."""
        if self.processor:
            await self.processor.stop()

    async def _create_processor(self) -> None:
        """Instantiates the processor using the stored config."""
        self.processor = await self.processor_type.create(
            **self.processor_config
        )

    async def append(self, event: Event) -> None:
        """Adds a new Event to the pile and marks it as pending.

        Args:
            event (Event): The event to add.
        """
        async with self.pile:
            self.pile.include(event)
            self.pending.include(event)

    @property
    def completed_events(self) -> Pile[Event]:
        """Pile[Event]: All events in COMPLETED status."""
        return Pile(
            collections=[
                e for e in self.pile if e.status == EventStatus.COMPLETED
            ],
            item_type=self.processor_type.event_type,
            strict_type=self.strict_event_type,
        )

    @property
    def pending_events(self) -> Pile[Event]:
        """Pile[Event]: All events currently in PENDING status."""
        return Pile(
            collections=[
                e for e in self.pile if e.status == EventStatus.PENDING
            ],
            item_type=self.processor_type.event_type,
            strict_type=self.strict_event_type,
        )

    @property
    def failed_events(self) -> Pile[Event]:
        """Pile[Event]: All events whose status is FAILED."""
        return Pile(
            collections=[
                e for e in self.pile if e.status == EventStatus.FAILED
            ],
            item_type=self.processor_type.event_type,
            strict_type=self.strict_event_type,
        )

    def __contains__(self, ref: ID[Event].Ref) -> bool:
        """Checks if a given Event or ID reference is present in the pile.

        Args:
            ref (ID[Event].Ref):
                A reference to an Event (e.g., the Event object, its ID, etc.).

        Returns:
            bool: True if the referenced event is in the pile, False otherwise.
        """
        return ref in self.pile


# File: lionagi/protocols/generic/processor.py

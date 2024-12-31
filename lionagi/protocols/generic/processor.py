# File: processor.py

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
    """
    A base class managing a queue of events with capacity-limited,
    asynchronous processing. Subclass this to provide custom event
    handling logic or permission checks.
    """

    event_type: ClassVar[type[Event]]

    def __init__(
        self,
        queue_capacity: int,
        capacity_refresh_time: float,
    ):
        """
        Args:
            queue_capacity (int):
                Max number of events processed in one batch.
            capacity_refresh_time (float):
                Time in seconds after which capacity is reset.
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
        """Current processing capacity."""
        return self._available_capacity

    @available_capacity.setter
    def available_capacity(self, value: int) -> None:
        self._available_capacity = value

    @property
    def execution_mode(self) -> bool:
        """Whether the processor is actively executing events."""
        return self._execution_mode

    @execution_mode.setter
    def execution_mode(self, value: bool) -> None:
        self._execution_mode = value

    async def enqueue(self, event: Event) -> None:
        """Add an event to the queue asynchronously."""
        await self.queue.put(event)

    async def dequeue(self) -> Event:
        """Retrieve the next event from the queue."""
        return await self.queue.get()

    async def join(self) -> None:
        """Block until the queue is empty and all tasks are done."""
        await self.queue.join()

    async def stop(self) -> None:
        """Signal to stop processing events."""
        self._stop_event.set()

    async def start(self) -> None:
        """Clear the stop signal, allowing event processing."""
        self._stop_event.clear()

    def is_stopped(self) -> bool:
        """Check if the processor is in a stopped state."""
        return self._stop_event.is_set()

    @classmethod
    async def create(cls, **kwargs: Any) -> "Processor":
        """
        Asynchronously construct a new processor instance.

        Args:
            **kwargs: Initialization arguments.

        Returns:
            Processor: A newly instantiated processor.
        """
        return cls(**kwargs)

    async def process(self) -> None:
        """
        Dequeue and process events up to the available capacity.
        Marks events as PROCESSING, invokes them, and waits for tasks
        to complete. Resets capacity afterward.
        """
        tasks = set()
        prev_event: Event = None

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
        """
        Decide if an event may proceed. By default, always returns True.
        Override for custom logic (e.g. rate limits, user checks, etc.).
        """
        return True

    async def execute(self) -> None:
        """
        Continuously process events until `stop()` is called. Respects
        capacity_refresh_time between cycles.
        """
        self.execution_mode = True
        await self.start()

        while not self.is_stopped():
            await self.process()
            await asyncio.sleep(self.capacity_refresh_time)

        self.execution_mode = False


class Executor(Observer):
    """
    Manages events via a Processor, holding them in a `Pile` until
    they can be forwarded. Subclass for custom behaviors.
    """

    processor_type: ClassVar[type[Processor]]

    def __init__(
        self,
        processor_config: dict[str, Any] = None,
        strict_event_type: bool = False,
    ):
        """
        Args:
            processor_config (dict[str, Any] | None):
                Configuration for creating the Processor.
            strict_event_type (bool):
                If True, the underlying Pile enforces exact event type.
        """
        self.processor_config = processor_config or {}
        self.pending = Progression()
        self.processor: Processor = None
        self.pile: Pile[Event] = Pile(
            item_type=self.processor_type.event_type,
            strict_type=strict_event_type,
        )

    @property
    def event_type(self) -> type[Event]:
        """Type of Event handled by the processor."""
        return self.processor_type.event_type

    @property
    def strict_event_type(self) -> bool:
        """Whether the Pile enforces exact matching for event types."""
        return self.pile.strict_type

    async def forward(self) -> None:
        """
        Forward all pending events from the pile to the processor,
        then call processor.process() for immediate handling.
        """
        while len(self.pending) > 0:
            event = self.pile.popleft()
            await self.processor.enqueue(event)

        await self.processor.process()

    async def start(self) -> None:
        """Initialize and start the processor if needed."""
        if not self.processor:
            await self._create_processor()
        await self.processor.start()

    async def stop(self) -> None:
        """Stop the processor if it exists."""
        if self.processor:
            await self.processor.stop()

    async def _create_processor(self) -> None:
        """Instantiate the processor using stored config."""
        self.processor = await self.processor_type.create(
            **self.processor_config
        )

    async def append(self, event: Event) -> None:
        """
        Add a new Event to the pile and mark it pending.

        Args:
            event (Event): The event to add.
        """
        async with self.pile:
            self.pile.include(event)
            self.pending.include(event)

    @property
    def completed_events(self) -> Pile[Event]:
        """All events whose status is COMPLETED."""
        return Pile(
            collections=[
                e for e in self.pile if e.status == EventStatus.COMPLETED
            ],
            item_type=self.processor_type.event_type,
            strict_type=self.strict_event_type,
        )

    @property
    def pending_events(self) -> Pile[Event]:
        """All events still in PENDING status."""
        return Pile(
            collections=[
                e for e in self.pile if e.status == EventStatus.PENDING
            ],
            item_type=self.processor_type.event_type,
            strict_type=self.strict_event_type,
        )

    @property
    def failed_events(self) -> Pile[Event]:
        """All events whose status is FAILED."""
        return Pile(
            collections=[
                e for e in self.pile if e.status == EventStatus.FAILED
            ],
            item_type=self.processor_type.event_type,
            strict_type=self.strict_event_type,
        )

    def __contains__(self, ref: ID[Event].Ref) -> bool:
        """Check if a given Event or event ID reference is in the pile."""
        return ref in self.pile

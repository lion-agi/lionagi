"""Mock processor implementation for testing."""

import asyncio
from typing import Any, Optional

from lionagi.action.processor import ActionProcessor
from lionagi.protocols.types import Event, EventStatus


class MockProcessor(ActionProcessor):
    """Mock processor for testing with controllable behavior."""

    def __init__(
        self,
        capacity: int = 10,
        refresh_time: float = 0.1,
        should_fail: bool = False,
        processing_time: float | None = None,
        max_retries: int = 3,
    ) -> None:
        """Initialize mock processor with configurable behavior.

        Args:
            capacity: Maximum concurrent processing capacity
            refresh_time: Processing cycle interval in seconds
            should_fail: Whether processor should simulate failures
            processing_time: Optional fixed processing time per action
            max_retries: Maximum number of retry attempts for failed actions
        """
        super().__init__(capacity=capacity, refresh_time=refresh_time)
        self.should_fail = should_fail
        self.processing_time = processing_time
        self.max_retries = max_retries
        self.processed_events: list[Event] = []
        self.failed_events: list[Event] = []
        self.retry_counts: dict[str, int] = {}
        self._active_tasks: set[asyncio.Task[None]] = set()

    async def process(self) -> None:
        """Process events with configurable behavior."""
        while not self.queue.empty():
            # Process up to capacity events concurrently
            while (
                len(self._active_tasks) < self.capacity
                and not self.queue.empty()
            ):
                event = await self.dequeue()
                event_id = str(event.id)

                if self.should_fail:
                    if event_id not in self.retry_counts:
                        self.retry_counts[event_id] = 0

                    if self.retry_counts[event_id] < self.max_retries:
                        self.retry_counts[event_id] += 1
                        event.status = EventStatus.FAILED
                        event.error = "Simulated failure"
                        self.failed_events.append(event)
                        await self.enqueue(event)  # Retry
                    else:
                        event.status = EventStatus.FAILED
                        event.error = "Max retries exceeded"
                        self.failed_events.append(event)
                else:
                    # Create task for event processing
                    task = asyncio.create_task(self._process_event(event))
                    self._active_tasks.add(task)
                    task.add_done_callback(self._active_tasks.discard)

            # Wait for some tasks to complete if at capacity
            if len(self._active_tasks) >= self.capacity:
                await asyncio.wait(
                    self._active_tasks, return_when=asyncio.FIRST_COMPLETED
                )

        # Wait for all remaining tasks to complete
        if self._active_tasks:
            await asyncio.wait(self._active_tasks)
            self._active_tasks.clear()

    async def _process_event(self, event: Event) -> None:
        """Process a single event."""
        try:
            if self.processing_time:
                # Use real sleep for timing tests
                await asyncio.sleep(self.processing_time)

            await event.invoke()

            if event.status == EventStatus.COMPLETED:
                self.processed_events.append(event)
            elif event.status == EventStatus.FAILED:
                self.failed_events.append(event)

        except Exception as e:
            event.status = EventStatus.FAILED
            event.error = str(e)
            self.failed_events.append(event)

    async def request_permission(self, **kwargs: Any) -> bool:
        """Mock permission check."""
        return not self.should_fail

    def reset(self) -> None:
        """Reset processor state."""
        self.processed_events.clear()
        self.failed_events.clear()
        self.retry_counts.clear()
        self.should_fail = False
        self._active_tasks.clear()

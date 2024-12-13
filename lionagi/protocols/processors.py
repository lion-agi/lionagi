# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import asyncio
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, NoReturn

from .base import Event, Observer

__all__ = (
    "BaseProcessor",
    "BaseExecutor",
)


class BaseProcessor(Observer):
    """Observers for information transformation and analysis."""

    event_type: type[Event]

    def __init__(self, capacity: int, refresh_time: float) -> None:
        if capacity < 0:
            raise ValueError("initial capacity must be >= 0")
        if refresh_time < 0:
            raise ValueError("refresh time for execution can not be negative")

        self.capacity = capacity
        self.queue = asyncio.Queue()
        self._stop_event = asyncio.Event()
        self.available_capacity = capacity
        self.execution_mode: bool = False
        self.refresh_time = refresh_time

    def is_stopped(self) -> bool:
        """
        Indicates whether the processor has been stopped.

        Returns:
            True if the processor has been stopped, otherwise False.
        """
        return self._stop_event.is_set()

    @classmethod
    def create(cls, **kwargs: Any) -> BaseProcessor:
        processor = cls(**kwargs)
        return processor

    @classmethod
    async def acreate(cls, **kwargs: Any) -> BaseProcessor:
        processor = cls(**kwargs)
        return processor

    async def enqueue(self, event: Event) -> None:
        await self.queue.put(item=event)

    async def dequeue(self) -> Event:
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

    @abstractmethod
    async def process(self) -> None:
        """process the event."""
        pass

    async def request_permission(self, **kwargs: Any) -> bool:
        return True

    async def execute(self) -> None:
        self.execution_mode = True
        await self.start()

        while not self.is_stopped():
            await self.process()
            await asyncio.sleep(self.refresh_time)
        self.execution_mode = False


@dataclass
class BaseExecutor(Observer):
    """Performing tasks with `processor`."""

    processor_class: type[BaseProcessor]
    strict: bool = True
    processor_config: dict[str, Any] = field(default_factory=dict)
    processor: BaseProcessor = None

    @abstractmethod
    async def forward(self, *args: Any, **kwargs: Any) -> Any:
        """Move onto the next step."""

    def create_processor(self) -> NoReturn:
        self.processor = self.processor_class.create(**self.processor_config)

    async def acreate_processor(self) -> NoReturn:
        self.processor = await self.processor_class.acreate(
            **self.processor_config
        )

    async def start(self) -> None:
        """Starts the event processor."""
        if not self.processor:
            await self.create_processor()
        await self.processor.start()

    async def stop(self) -> None:
        """Stops the event processor."""
        if self.processor:
            await self.processor.stop()

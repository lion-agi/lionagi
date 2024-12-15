# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from typing import ClassVar, TypeAlias

from typing_extensions import override

from ..protocols.base import EventStatus
from ..protocols.processors import BaseProcessor
from .base import Action

TaskSet: TypeAlias = set[asyncio.Task[None]]

__all__ = ("ActionProcessor",)


class ActionProcessor(BaseProcessor):
    """Processes queued actions asynchronously with capacity management.

    Handles action lifecycle from queue to completion, managing concurrency
    limits and optional permission checks before processing.
    """

    event_type: ClassVar[type[Action]] = Action

    @override
    async def process(self) -> None:
        """Process queued work items up to capacity limit.

        Executes actions concurrently within capacity constraints. Actions
        require permission before processing and are tracked through completion.
        """
        tasks: TaskSet = set()
        prev: Action | None = None
        next: Action | None = None

        while self.available_capacity > 0 and self.queue.qsize() > 0:
            if prev and prev.status == EventStatus.PENDING:
                next = prev
                await asyncio.sleep(self.refresh_time)
            else:
                next: Action = await self.dequeue()

            if await self.request_permission(**next.request):
                next.status = EventStatus.PROCESSING
                task = asyncio.create_task(next.invoke())
                tasks.add(task)
            prev = next

        if tasks:
            await asyncio.wait(tasks)
            self.available_capacity = self.capacity

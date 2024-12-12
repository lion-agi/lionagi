# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio

from typing_extensions import override

from ..protocols.base import EventStatus
from ..protocols.processors import BaseProcessor
from .base import Action


class ActionProcessor(BaseProcessor):
    """
    A processor class for processing action invokations.

    The `ActionProcessor` manages a queue of actions, processing them according
    to the specified capacity and refresh time. It handles the lifecycle of
    actions from enqueuing to processing and stopping. Optionally, it can
    request permission before processing each action.
    """

    observation_type = Action

    @override
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


__all__ = ["ActionProcessor"]

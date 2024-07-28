from __future__ import annotations

import asyncio
import logging

from typing import NoReturn, override

from lion_core.abc import Action
from lion_core.action.status import ActionStatus
from lion_core.action.action_processor import ActionProcessor
from lion_core.action.action_executor import ActionExecutor

from lionagi.os.service.config import DEFAULT_RATE_LIMIT_CONFIG
from lionagi.os.service.api_calling import APICalling
from lionagi.os.service.endpoint.status_tracker import StatusTracker


class RateLimitedProcessor(ActionProcessor):

    @override
    def __init__(
        self,
        interval: int | None = None,
        interval_request: int | None = None,
        interval_token: int | None = None,
        refresh_time: float = 1,
    ):
        interval = interval or DEFAULT_RATE_LIMIT_CONFIG["interval"]
        interval_request = (
            interval_request or DEFAULT_RATE_LIMIT_CONFIG["interval_request"]
        )
        interval_token = interval_token or DEFAULT_RATE_LIMIT_CONFIG["interval_token"]

        super().__init__(interval_request, refresh_time)

        self.interval = interval
        self.interval_token = interval_token or 1_000_000
        self.available_token_capacity: int = interval_token or 1_000_000
        self._rate_limit_replenisher_task: asyncio.Task | None = None
        self._lock: asyncio.Lock = asyncio.Lock()

    async def start_replenishing(self) -> NoReturn:
        """Start replenishing rate limit capacities at regular intervals."""
        try:
            while not self._stop_event.is_set():
                await asyncio.sleep(self.interval)
                async with self._lock:
                    self.available_request_capacity = self.capacity
                    self.available_token_capacity = self.interval_token
        except asyncio.CancelledError:
            logging.info("Rate limit replenisher task cancelled.")
        except Exception as e:
            logging.error(f"Error in rate limit replenisher: {e}")

    async def stop_replenishing(self) -> None:
        """Stop the replenishment task."""
        if self._rate_limit_replenisher_task:
            self._rate_limit_replenisher_task.cancel()
            await self._rate_limit_replenisher_task
        await self.stop()

    async def request_permission(self, required_tokens: int) -> bool:
        async with self._lock:
            if self.available_capacity > 0 and self.available_token_capacity > 0:
                self.available_capacity -= 1
                self.available_token_capacity -= required_tokens
                return True
            return False

    @override
    async def process(self) -> None:
        """Process the work items in the queue."""
        tasks = set()

        while self.available_capacity > 0 and self.queue.qsize() > 0:
            next: APICalling = await self.dequeue()

            while not await self.request_permission(
                next.content.get(["required_tokens"])
            ):
                await asyncio.sleep(1)

            next.status = ActionStatus.PROCESSING
            task = asyncio.create_task(next.invoke())
            tasks.add(task)

        if tasks:
            await asyncio.wait(tasks)
            self.available_capacity = self.capacity

    @classmethod
    async def create(
        cls,
        interval: int = None,
        interval_request: int = None,
        interval_token: int = None,
        refresh_time: float = 1,
    ) -> RateLimitedProcessor:
        self = cls(
            interval=interval,
            interval_request=interval_request,
            interval_token=interval_token,
            refresh_time=refresh_time,
        )
        self._rate_limit_replenisher_task = asyncio.create_task(
            self.start_replenishing()
        )
        return self


class RateLimitedExecutor(ActionExecutor):

    def __init__(
        self,
        interval: int | None = None,
        interval_request: int | None = None,
        interval_token: int | None = None,
        refresh_time: int = 1,
    ):

        super().__init__(
            capacity=interval_request,
            refresh_time=refresh_time,
            processor_class=RateLimitedProcessor,
            interval=interval,
            interval_request=interval_request,
            interval_token=interval_token,
        )
        self.status_tracker = StatusTracker()
        self._has_initialized = False

    async def init_processor(self):
        self.processor: RateLimitedProcessor = await self.processor_class.create(
            *self.processor_config["args"], **self.processor_config["kwargs"]
        )
        self._has_initialized = True

    async def add_action(
        self,
        payload: dict = None,
        base_url: str = None,
        endpoint: str = None,
        api_key: str = None,
        method="post",
        content=None,
        required_tokens=15,
    ) -> APICalling:

        action = APICalling(
            payload=payload,
            base_url=base_url,
            endpoint=endpoint,
            api_key=api_key,
            method=method,
            content=content,
            required_tokens=required_tokens,
        )

        self.pile += action
        return action

    @override
    async def forward(self):
        """
        Forwards pending action items to the queue.
        """
        while len(self.pending) > 0:
            action: Action = self.pile[self.pending.popleft()]
            await self.processor.enqueue(action)


# File: lionagi/os/service/api/rate_limited_processor.py

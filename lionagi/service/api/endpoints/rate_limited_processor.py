# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
from typing import Self

from typing_extensions import override

from lionagi.protocols.generic.processor import Executor, Processor

from .base import APICalling

__all__ = (
    "RateLimitedAPIProcessor",
    "RateLimitedAPIExecutor",
)


class RateLimitedAPIProcessor(Processor):

    event_type = APICalling

    def __init__(
        self,
        queue_capacity: int,
        capacity_refresh_time: float,
        interval: float | None = None,
        limit_requests: int = None,
        limit_tokens: int = None,
    ):
        super().__init__(queue_capacity, capacity_refresh_time)
        self.limit_tokens = limit_tokens
        self.limit_requests = limit_requests
        self.interval = interval or self.capacity_refresh_time
        self.available_request = self.limit_requests
        self.available_token = self.limit_tokens
        self._rate_limit_replenisher_task: asyncio.Task | None = None
        self._lock: asyncio.Lock = asyncio.Lock()

    async def start_replenishing(self):
        """Start replenishing rate limit capacities at regular intervals."""
        await self.start()
        try:
            while not self.is_stopped():
                await asyncio.sleep(delay=self.interval)
                async with self._lock:
                    if self.limit_requests is not None:
                        self.available_request = (
                            self.limit_requests - self.queue.qsize()
                        )
                    if self.limit_tokens is not None:
                        self.available_token = self.limit_tokens

        except asyncio.CancelledError:
            logging.info("Rate limit replenisher task cancelled.")
        except Exception as e:
            logging.error(f"Error in rate limit replenisher: {e}")

    @override
    async def stop(self) -> None:
        """Stop the replenishment task."""
        if self._rate_limit_replenisher_task:
            self._rate_limit_replenisher_task.cancel()
            await self._rate_limit_replenisher_task
        await super().stop()

    @override
    @classmethod
    async def create(
        cls,
        queue_capacity: int,
        capacity_refresh_time: float,
        interval: float | None = None,
        limit_requests: int = None,
        limit_tokens: int = None,
    ) -> Self:
        self = cls(
            interval=interval,
            queue_capacity=queue_capacity,
            capacity_refresh_time=capacity_refresh_time,
            limit_requests=limit_requests,
            limit_tokens=limit_tokens,
        )
        self._rate_limit_replenisher_task = asyncio.create_task(
            self.start_replenishing()
        )
        return self

    @override
    async def request_permission(self, required_tokens: int = None) -> bool:
        async with self._lock:
            if self.limit_requests is None and self.limit_tokens is None:
                if self.queue.qsize() < self.queue_capacity:
                    return True

            if self.limit_requests is not None:
                if self.available_request > 0:
                    self.available_request -= 1
                if required_tokens is None:
                    return True
                else:
                    if self.limit_tokens >= required_tokens:
                        self.limit_tokens -= required_tokens
                        return True

            if self.limit_tokens is not None:
                if required_tokens is None:
                    return True
                if self.limit_tokens >= required_tokens:
                    self.limit_tokens -= required_tokens
                    return True

            return False


class RateLimitedAPIExecutor(Executor):

    processor_type = RateLimitedAPIProcessor

    def __init__(
        self,
        queue_capacity: int,
        capacity_refresh_time: float,
        interval: float | None = None,
        limit_requests: int = None,
        limit_tokens: int = None,
        strict_event_type: bool = False,
    ):
        config = {
            "queue_capacity": queue_capacity,
            "capacity_refresh_time": capacity_refresh_time,
            "interval": interval,
            "limit_requests": limit_requests,
            "limit_tokens": limit_tokens,
        }

        self.config = config
        self.interval = interval
        self.limit_requests = limit_requests
        self.limit_tokens = limit_tokens

        super().__init__(
            processor_config=config, strict_event_type=strict_event_type
        )

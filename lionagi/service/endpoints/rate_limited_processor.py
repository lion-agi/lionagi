# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging

from typing_extensions import Self, override

from lionagi.protocols.generic.processor import (
    Executor,
    Processor,
    ProcessorConfig,
)

from .base import APICalling

__all__ = (
    "RateLimitedAPIProcessor",
    "RateLimitedAPIExecutor",
)


class RateLimitedProcessorConfig(ProcessorConfig):

    interval: float | None = 60
    limit_requests: int = None
    limit_tokens: int = None


class RateLimitedAPIProcessor(Processor):

    event_type = APICalling
    config_type = RateLimitedProcessorConfig

    def __init__(self, config: RateLimitedProcessorConfig):
        super().__init__(config)
        self.limit_tokens = config.limit_tokens
        self.limit_requests = config.limit_requests
        self.interval = config.interval or self.capacity_refresh_time
        self.available_request = self.limit_requests
        self.available_token = self.limit_tokens
        self._lock: asyncio.Lock = asyncio.Lock()
        self._rate_limit_replenisher_task: asyncio.Task | None = None

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
        concurrency_limit: int | None = None,
    ) -> Self:
        self = cls(
            interval=interval,
            queue_capacity=queue_capacity,
            capacity_refresh_time=capacity_refresh_time,
            limit_requests=limit_requests,
            limit_tokens=limit_tokens,
            concurrency_limit=concurrency_limit,
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
        processor_config: RateLimitedProcessorConfig = None,
        strict_event_type: bool = False,
        queue_capacity: int = None,
        capacity_refresh_time: float = None,
        interval: float | None = None,
        limit_requests: int = None,
        limit_tokens: int = None,
        concurrency_limit: int | None = None,
    ):
        super().__init__(**{k: v for k, v in locals().items if k != "self"})

    @property
    def interval(self) -> float:
        return self.processor_config.interval

    @property
    def limit_requests(self) -> int:
        return self.processor_config.limit_requests

    @property
    def limit_tokens(self) -> int:
        self.processor_config.limit_tokens

import asyncio
import logging
from lion_core.action.action_queue import ActionQueue
from lionagi.os.service.config import (
    DEFAULT_RATE_LIMIT_CONFIG,
    CACHED_CONFIG,
    RETRY_CONFIG,
)


class RateLimiter:

    def __init__(
        self,
        interval: int = None,
        interval_requests: int = None,
        interval_tokens: int = None,
        max_concurrent: int = None,
        refresh_time: int = 0.5,
    ) -> None:

        self.interval = interval or DEFAULT_RATE_LIMIT_CONFIG["interval"]
        self.interval_requests = (
            interval_requests or DEFAULT_RATE_LIMIT_CONFIG["interval_request"]
        )
        self.interval_tokens = (
            interval_tokens or DEFAULT_RATE_LIMIT_CONFIG["interval_token"]
        )
        self.queue = ActionQueue(max_concurrent or self.interval_requests, refresh_time)
        self._rate_limit_replenisher_task: asyncio.Task | None = None
        self._stop_replenishing: asyncio.Event = asyncio.Event()
        self._lock: asyncio.Lock = asyncio.Lock()

    async def start_replenishing(self):
        """Start replenishing rate limit capacities at regular intervals."""
        try:
            while not self._stop_replenishing.is_set():
                await asyncio.sleep(self.interval)
                async with self._lock:
                    self.available_request_capacity = self.interval_requests
                    self.available_token_capacity = self.interval_tokens
        except asyncio.CancelledError:
            logging.info("Rate limit replenisher task cancelled.")
        except Exception as e:
            logging.error(f"Error in rate limit replenisher: {e}")

    async def request_permission(self, required_tokens: int) -> bool:
        async with self._lock:
            if (
                self.available_request_capacity > 0
                and self.available_token_capacity > 0
            ):
                self.available_request_capacity -= 1
                self.available_token_capacity -= required_tokens
                return True
            return False


class RateLimiter:

    def __init__(
        self,
        interval: int = 60,
        interval_requests: int = 10_000,
        interval_tokens: int = 1_000_000,
    ) -> None:
        pass

        self.interval = interval
        self.interval_requests = interval_requests
        self.interval_tokens = interval_tokens
        self.tokens = self.interval_tokens


"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import asyncio
from lionagi.core.work.work import WorkStatus

import logging
import asyncio
from typing_extensions import override

from lion_core.action.action_processor import ActionProcessor
from lion_core.action.action_executor import ActionExecutor
from lion_core.action.status import ActionStatus

from lionagi.os.service.config import DEFAULT_RATE_LIMIT_CONFIG, RETRY_CONFIG
from lionagi.os.service.api_calling import APICalling


class RateLimitedProcessor(ActionProcessor):

    def __init__(
        self,
        interval: int | None = None,
        interval_request: int | None = None,
        interval_token: int | None = None,
        refresh_time: float = None,
        concurrent_capacity: int = None,
    ):
        super().__init__(
            capacity=concurrent_capacity or interval_request,
            refresh_time=refresh_time,
        )
        self.interval = interval
        self.interval_token = interval_token
        self.interval_request = interval_request
        self.available_request = self.interval_request
        self.available_token = self.interval_token
        self._rate_limit_replenisher_task: asyncio.Task | None = None
        self._lock: asyncio.Lock = asyncio.Lock()

    @override
    async def start_replenishing(self):
        """Start replenishing rate limit capacities at regular intervals."""
        await self.start()
        try:
            while not self.stopped:
                await asyncio.sleep(delay=self.interval)
                async with self._lock:
                    self.available_request = self.interval_request - self.queue.qsize()
                    self.available_token = self.interval_token

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
    async def request_permission(self, required_tokens: int) -> bool:
        async with self._lock:
            if self.available_capacity > 0 and self.available_token > 0:
                self.available_request -= 1
                self.available_token -= required_tokens
                return True
            return False

    @override
    @classmethod
    async def create(
        cls,
        interval: int,
        interval_request: int,
        interval_token: int,
        refresh_time: float,
        concurrent_capacity: int,
    ) -> "RateLimitedProcessor":
        self = cls(
            interval=interval,
            interval_request=interval_request,
            interval_token=interval_token,
            refresh_time=refresh_time,
            concurrent_capacity=concurrent_capacity,
        )
        self._rate_limit_replenisher_task = asyncio.create_task(
            self.start_replenishing()
        )
        return self


class RateLimitedExecutor(ActionExecutor):

    processor_class = RateLimitedProcessor

    def __init__(
        self,
        interval: int | None = None,
        interval_request: int | None = None,
        interval_token: int | None = None,
        refresh_time: float | None = None,
        concurrent_capacity: int = None,
    ):
        config = {
            "interval": interval,
            "interval_request": interval_request,
            "interval_token": interval_token,
            "refresh_time": refresh_time,
            "concurrent_capacity": concurrent_capacity,
        }
        for k, v in config.items():
            if v is None:
                config[k] = DEFAULT_RATE_LIMIT_CONFIG[k]

        super().__init__(**config)

    @staticmethod
    def create_api_calling(
        payload: dict = None,
        base_url: str = None,
        endpoint: str = None,
        api_key: str = None,
        method="post",
        retry_config=RETRY_CONFIG,
    ):
        action = APICalling(
            payload=payload,
            base_url=base_url,
            endpoint=endpoint,
            api_key=api_key,
            method=method,
            retry_config=retry_config,
        )
        return action

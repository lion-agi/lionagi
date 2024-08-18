import logging
import asyncio

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
        refresh_time: float = 1,
    ):
        super().__init__(
            capacity=interval_request,
            refresh_time=refresh_time,
        )
        self.interval = interval
        self.interval_token = interval_token
        self._rate_limit_replenisher_task: asyncio.Task | None = None
        self._lock: asyncio.Lock = asyncio.Lock()
        self.available_request_capacity = self.capacity
        self.available_token_capacity = self.interval_token

    async def start_replenishing(self):
        """Start replenishing rate limit capacities at regular intervals."""
        try:
            while not self.stopped:
                await asyncio.sleep(delay=self.interval)
                async with self._lock:
                    self.available_request_capacity = self.available_capacity
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
                self.available_request_capacity -= 1
                self.available_token_capacity -= required_tokens
                return True
            return False

    async def process(self) -> None:
        """Process the work items in the queue."""
        tasks = set()
        prev = None

        while self.available_capacity > 0 and self.queue.qsize() > 0:
            if prev and prev.status == ActionStatus.PROCESSING:
                next = prev
            else:
                next = await self.dequeue()
                next.status = ActionStatus.PROCESSING

            if await self.request_permission(next.required_tokens):
                task = asyncio.create_task(next.invoke())
                tasks.add(task)
                prev = next

        if tasks:
            await asyncio.wait(tasks)
            self.available_capacity = self.capacity

    @classmethod
    async def create(
        cls,
        interval: int,
        interval_request: int,
        interval_token: int,
        refresh_time: float,
    ):
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
        interval: int | None = DEFAULT_RATE_LIMIT_CONFIG["interval"],
        interval_request: int | None = DEFAULT_RATE_LIMIT_CONFIG["interval_request"],
        interval_token: int | None = DEFAULT_RATE_LIMIT_CONFIG["interval_token"],
        refresh_time: float = 1,
    ):
        super().__init__(
            interval=interval,
            interval_request=interval_request,
            interval_token=interval_token,
            refresh_time=refresh_time,
        )
        self.processor = None

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

    async def create_processor(self):
        self.processor = await RateLimitedProcessor.create(**self.processor_config)

    async def stop(self):
        await self.processor.stop_replenishing()

    async def forward(self):
        while len(self.pending) > 0:
            work = self.pile[self.pending.popleft()]
            await self.processor.enqueue(work)

    async def process(self):
        await self.forward()
        await self.processor.process()

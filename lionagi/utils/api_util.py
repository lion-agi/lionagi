import asyncio
from dataclasses import dataclass
from abc import ABC, abstractmethod

class AsyncQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
    
    async def enqueue(self, item):
        await self.queue.put(item)
    
    async def dequeue(self):
        return await self.queue.get()
    
    def task_done(self):
        self.queue.task_done()
    
    async def join(self):
        await self.queue.join()

@dataclass
class StatusTracker:
    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_rate_limit_errors: int = 0
    num_api_errors: int = 0
    num_other_errors: int = 0
    
class RateLimiter:
    def __init__(self, max_requests_per_minute: int, max_tokens_per_minute: int):
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_minute = max_tokens_per_minute
        self.available_request_capacity = max_requests_per_minute
        self.available_token_capacity = max_tokens_per_minute
        self.request_queue = AsyncQueue()
        self._stop_event = asyncio.Event()
        self.rate_limit_replenisher_task = asyncio.create_task(self.rate_limit_replenisher())

    async def rate_limit_replenisher(self, interval=60):
        while not self._stop_event.is_set():
            await asyncio.sleep(interval)
            self.available_request_capacity = self.max_requests_per_minute
            self.available_token_capacity = self.max_tokens_per_minute

    async def enqueue_and_handle_request(self, request_coroutine):
        tokens_used = await self.num_tokens_required_by_request(request_coroutine)
        if tokens_used is None:
            return None
        await self.request_queue.enqueue((request_coroutine, tokens_used))
        return await self.handle_next_request()

    async def handle_next_request(self):
        request_coroutine, tokens_used = await self.request_queue.dequeue()
        try:
            if self.available_request_capacity > 0 and self.available_token_capacity >= tokens_used:
                self.available_request_capacity -= 1
                self.available_token_capacity -= tokens_used
                response = await request_coroutine()
            else:
                await asyncio.sleep(1)
                await self.request_queue.enqueue((request_coroutine, tokens_used))
                return None
        finally:
            self.request_queue.task_done()
        return response

    @abstractmethod
    async def num_tokens_required_by_request(self, request_coroutine):
        pass

    async def stop(self):
        self._stop_event.set()
        await self.rate_limit_replenisher_task

class BaseAPIService(ABC):
    def __init__(self, rate_limiter: RateLimiter, api_key: str, token_encoding_name: str, max_attempts: int, status_tracker: StatusTracker):
        self.rate_limiter = rate_limiter
        self.api_key = api_key
        self.token_encoding_name = token_encoding_name
        self.max_attempts = max_attempts
        self.status_tracker = status_tracker

    @abstractmethod
    async def call_api_endpoint(self, endpoint:str, **kwargs):
        pass

    @staticmethod
    def task_id_generator_function():
        """Generate integers 0, 1, 2, and so on."""
        task_id = 0
        while True:
            yield task_id
            task_id += 1
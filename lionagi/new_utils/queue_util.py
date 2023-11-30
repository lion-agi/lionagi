import asyncio
from dataclasses import dataclass
from abc import ABC, abstractmethod

# tested - works
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

# tested - works
@dataclass
class StatusTracker:
    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_rate_limit_errors: int = 0
    num_api_errors: int = 0
    num_other_errors: int = 0
    
    
    
## ---- todo

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
                # Pauses the current task, allowing other tasks to run
                await asyncio.sleep(1)
                # Re-enqueue the task back, if the condition is not met
                await self.request_queue.enqueue((request_coroutine, tokens_used))
                return None
        finally:
            self.request_queue.task_done()
        return response

    async def num_tokens_required_by_request(self, request_json):
        # Implementation of token counting logic to be filled in
        pass

    async def stop(self):
        self._stop_event.set()
        await self.request_queue.enqueue((None, 0))

async def main():
    rate_limiter = RateLimiter(max_requests_per_minute=5, max_tokens_per_minute=100)
    # Do something with the rate_limiter, like enqueueing tasks
    # ...
    # Don't forget to call `rate_limiter.stop()` when you're done
    await rate_limiter.stop()

if __name__ == "__main__":
    asyncio.run(main())


class OpenAIRateLimiter(RateLimiter):
    def __init__(self, max_requests_per_minute: int, max_tokens_per_minute: int):
        super().__init__(max_requests_per_minute, max_tokens_per_minute)
        self._stop_event = asyncio.Event()

    async def rate_limit_replenisher(self, interval=60):
        while not self._stop_event.is_set():
            await asyncio.sleep(interval)
            # Assuming the replenishment sets the available requests and tokens to max
            # This example assumes requests are handled one by one, you may need a more complex design
            await self.process_queue_items()

    async def process_queue_items(self):
        # Logic to process items from the queue, subject to rate limits
        # This example does not include the actual rate limit enforcement logic,
        # which should regulate when requests are dequeued and handled.
        pass

    async def stop(self):
        self._stop_event.set()
        await self.request_queue.enqueue((None, 0))  # Signal stop to the queue

# Use these classes together as needed with your logic
# Here is a skeleton to demonstrate how you might integrate them in an async function

async def main():
    rate_limiter = OpenAIRateLimiter(max_requests_per_minute=5, max_tokens_per_minute=100)
    # Do something with the rate_limiter, for example enqueue tasks
    # Don't forget to call `rate_limiter.stop()` when you're done to cleanly shut down the replenisher task

    # Still, this is just a skeleton. Actual rate limiting logic, task scheduling, and error handling
    # should be implemented within these classes or when using them.

if __name__ == "__main__":
    asyncio.run(main())




# ------
import asyncio
import httpx
import logging
import tiktoken


class OpenAIRateLimiter(RateLimiter):
    def __init__(self, max_requests_per_minute: int, max_tokens_per_minute: int):
        super().__init__(max_requests_per_minute, max_tokens_per_minute)
        self._request_queue = asyncio.Queue()
        self._stop_event = asyncio.Event()

    async def enqueue_and_handle_request(self, request_coroutine, tokens_used: int = 0):
        async with self._request_queue.mutex:
            if self.available_request_capacity > 0 and self.available_token_capacity >= tokens_used:
                self.available_request_capacity -= 1
                self.available_token_capacity -= tokens_used
                response = await request_coroutine()
                self.available_request_capacity += 1
                self.available_token_capacity += tokens_used
                return response
            else:
                await self.rate_limit_replenisher_task

    async def rate_limit_replenisher(self, interval=60):
        while not self._stop_event.is_set():
            await asyncio.sleep(interval)
            self.available_request_capacity = self.max_requests_per_minute
            self.available_token_capacity = self.max_tokens_per_minute

    async def stop(self):
        self._stop_event.set()
        await self._request_queue.put(None)
        
    def num_tokens_consumed_from_request(self, request_json: dict, api_endpoint: str):
        """Count the number of tokens in the request. Only supports completion and embedding requests."""
        encoding = tiktoken.get_encoding(self.token_encoding_name)
        # if completions request, tokens = prompt + n * max_tokens
        if api_endpoint.endswith("completions"):
            max_tokens = request_json.get("max_tokens", 15)
            n = request_json.get("n", 1)
            completion_tokens = n * max_tokens

            # chat completions
            if api_endpoint.startswith("chat/"):
                num_tokens = 0
                for message in request_json["messages"]:
                    num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                    for key, value in message.items():
                        num_tokens += len(encoding.encode(value))
                        if key == "name":  # if there's a name, the role is omitted
                            num_tokens -= 1  # role is always required and always 1 token
                num_tokens += 2  # every reply is primed with <im_start>assistant
                return num_tokens + completion_tokens
            # normal completions
            else:
                prompt = request_json["prompt"]
                if isinstance(prompt, str):  # single prompt
                    prompt_tokens = len(encoding.encode(prompt))
                    num_tokens = prompt_tokens + completion_tokens
                    return num_tokens
                elif isinstance(prompt, list):  # multiple prompts
                    prompt_tokens = sum([len(encoding.encode(p)) for p in prompt])
                    num_tokens = prompt_tokens + completion_tokens * len(prompt)
                    return num_tokens
                else:
                    raise TypeError(
                        'Expecting either string or list of strings for "prompt" field in completion request'
                    )
        # if embeddings request, tokens = input tokens
        elif api_endpoint == "embeddings":
            input = request_json["input"]
            if isinstance(input, str):  # single input
                num_tokens = len(encoding.encode(input))
                return num_tokens
            elif isinstance(input, list):  # multiple inputs
                num_tokens = sum([len(encoding.encode(i)) for i in input])
                return num_tokens
            else:
                raise TypeError(
                    'Expecting either string or list of strings for "inputs" field in embedding request'
                )
        # more logic needed to support other API calls (e.g., edits, inserts, DALL-E)
        else:
            raise NotImplementedError(
                f'API endpoint "{api_endpoint}" not implemented in this script'
            )
        

class OpenAIService(BaseAPIService):
    base_url = "https://api.openai.com/v1/"

    def __init__(self, api_key, rate_limiter, token_encoding_name, max_attempts, status_tracker):
        super().__init__(api_key, rate_limiter, token_encoding_name, max_attempts, status_tracker)

    async def call_api_endpoint(self, endpoint: str, **kwargs):
        # Let each endpoint method handle token counting based on request specifics
        tokens_used = kwargs.pop('tokens_used', 0)
        payload = kwargs
        url = f"{self.base_url}{endpoint}"
        headers = {'Authorization': f'Bearer {self.api_key}'}
        method = kwargs.pop('method', 'POST')

        for attempt in range(self.max_attempts):
            try:
                # Use the shared rate limiter instance to handle OpenAI API rate limits
                request_coroutine = lambda: httpx.post(url=url, headers=headers, json=payload)
                response = await self.rate_limiter.enqueue_and_handle_request(request_coroutine, tokens_used=tokens_used)
                if response.status_code == 200:
                    self.status_tracker.num_tasks_succeeded += 1
                    return response.json()
                elif response.status_code == 429:
                    self.status_tracker.num_rate_limit_errors += 1
                    await asyncio.sleep(10)  # Simple backoff strategy, consider using Retry-After header
                else:
                    self.status_tracker.num_api_errors += 1
            except Exception as error:
                self.status_tracker.num_other_errors += 1
                logging.warning(f"API call to {endpoint} failed with exception: {error}")
        logging.error(f"Request to {url} failed after {self.max_attempts} attempts.")
        return None
    
oai_status_tracker = StatusTracker()
oai_rate_limiter = OpenAIRateLimiter(max_requests_per_minute=500, max_tokens_per_minute=300000)
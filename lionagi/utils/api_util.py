import asyncio
import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generator, NoReturn, Optional

@dataclass
class StatusTracker:
    """Class for keeping track of various task statuses.
    
    This class serves as a simple way to monitor different types of task
    outcomes and errors within a system. It uses dataclasses for easy
    creation and management of state.
    
    Attributes:
        num_tasks_started: The number of tasks that have been initiated.
        num_tasks_in_progress: The number of tasks currently being processed.
        num_tasks_succeeded: The number of tasks that have completed successfully.
        num_tasks_failed: The number of tasks that have failed.
        num_rate_limit_errors: The number of tasks that failed due to rate limiting.
        num_api_errors: The number of tasks that failed due to API errors.
        num_other_errors: The number of tasks that failed due to other errors.
    """
    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_rate_limit_errors: int = 0
    num_api_errors: int = 0
    num_other_errors: int = 0


class AsyncQueue:
    """
    A queue class that handles asynchronous operations using asyncio.

    This class provides an asynchronous queue that can enqueue items, process them
    asynchronously, and support graceful shutdowns. It is designed to facilitate
    concurrent task processing in an orderly and controlled manner.

    Attributes:
        queue (asyncio.Queue): A queue to hold items for asynchronous processing.
        _stop_event (asyncio.Event): An event to signal when the queue should stop processing.

    Methods:
        enqueue(item): Add an item to the queue for processing.
        dequeue(): Remove and return an item from the queue.
        join(): Wait until all items in the queue have been processed.
        stop(): Signal to stop processing new items in the queue.
        stopped(): Check if the queue has been signaled to stop.
        process_requests(func): Process items using a provided function.
    """

    def __init__(self) -> None:
        """
        Initializes an AsyncQueue object with an empty asyncio Queue and a stop event.
        """
        self.queue = asyncio.Queue()
        self._stop_event = asyncio.Event()

    async def enqueue(self, item: Any) -> None:
        """
        Asynchronously add an item to the queue for processing.

        Args:
            item (Any): The item to be added to the queue.

        Example:
            >>> async_queue = AsyncQueue()
            >>> asyncio.run(async_queue.enqueue('Task 1'))
        """
        await self.queue.put(item)

    async def dequeue(self) -> Any:
        """
        Asynchronously remove and return an item from the queue.

        If the queue is empty, this method will wait until an item is available.

        Returns:
            Any: The next item from the queue.

        Example:
            >>> async_queue = AsyncQueue()
            >>> asyncio.run(async_queue.enqueue('Task 1'))
            >>> asyncio.run(async_queue.dequeue())
            'Task 1'
        """
        return await self.queue.get()

    async def join(self) -> None:
        """
        Asynchronously wait until all items in the queue have been processed.

        This method blocks until every item that has been enqueued is processed, 
        ensuring that all tasks are completed.

        Example:
            >>> async_queue = AsyncQueue()
            >>> asyncio.run(async_queue.enqueue('Task 1'))
            >>> asyncio.run(async_queue.join())  # This will block until 'Task 1' is processed.
        """
        await self.queue.join()

    async def stop(self) -> None:
        """
        Signal the queue to stop processing new items.

        Once called, the queue will not process any new items after the current ones
        are completed, allowing for a graceful shutdown.

        Example:
            >>> async_queue = AsyncQueue()
            >>> asyncio.run(async_queue.stop())  # This signals the queue to stop processing.
        """
        self._stop_event.set()

    def stopped(self) -> bool:
        """
        Check if the queue has been signaled to stop processing.

        Returns:
            bool: True if a stop has been signaled, False otherwise.

        Example:
            >>> async_queue = AsyncQueue()
            >>> asyncio.run(async_queue.stop())
            >>> async_queue.stopped()
            True
        """
        return self._stop_event.is_set()

    async def process_requests(self, func: Callable[[Any], Any]) -> None:
        """
        Asynchronously process items from the queue using the provided function.

        Continuously dequeues items and applies the given function to each. 
        The processing stops when the queue is signaled to stop or a sentinel value (`None`) is dequeued.

        Args:
            func (Callable[[Any], Any]): A coroutine function to process items from the queue.

        Example:
            >>> async def sample_processing(task):
            ...     print("Processing:", task)
            >>> async_queue = AsyncQueue()
            >>> asyncio.run(async_queue.enqueue('Task 1'))
            >>> asyncio.run(async_queue.process_requests(sample_processing))
            Processing: Task 1
        """
        while not self.stopped():
            item = await self.dequeue()
            if item is None:  # Using `None` as a sentinel value to cease processing.
                await self.stop()
                break
            await func(item)


class RateLimiter(ABC):
    """
    An abstract base class for rate limiting mechanisms.

    This class defines a structure for rate limiters, which are used to control the frequency
    of requests sent to or received from a network interface controller or an API.

    Attributes:
        max_requests_per_minute (int): Maximum number of requests permitted per minute.
        max_tokens_per_minute (int): Maximum number of tokens that can accumulate per minute.
        available_request_capacity (int): Current number of available request slots.
        available_token_capacity (int): Current number of available tokens.
        rate_limit_replenisher_task (asyncio.Task): Background task for replenishing rate limits.

    Methods:
        rate_limit_replenisher: Coroutine to replenish rate limits over time.
        calculate_num_token: Method to calculate required tokens for a request.
    """
    
    def __init__(self, max_requests_per_minute: int, max_tokens_per_minute: int) -> None:
        """
        Initializes the RateLimiter with specified maximum request and token limits.

        Args:
            max_requests_per_minute (int): Maximum requests allowed per minute.
            max_tokens_per_minute (int): Maximum tokens allowed to accumulate per minute.

        Example:
            >>> class MyRateLimiter(RateLimiter):
            ...     async def rate_limit_replenisher(self) -> NoReturn:
            ...         # Implementation for rate replenishment.
            ...     def calculate_num_token(self, payload: Dict[str, Any], api_endpoint: str) -> int:
            ...         # Implementation for token calculation.
            ...
            >>> limiter = MyRateLimiter(100, 200)
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_minute = max_tokens_per_minute
        self.available_request_capacity = max_requests_per_minute
        self.available_token_capacity = max_tokens_per_minute
    
    @abstractmethod
    async def rate_limit_replenisher(self) -> NoReturn:
        """
        Asynchronously replenishes rate limit capacities.

        This coroutine should be implemented to periodically restore `available_request_capacity`
        and `available_token_capacity` according to specific rules defined in subclasses.

        Example:
            >>> class MyRateLimiter(RateLimiter):
            ...     async def rate_limit_replenisher(self) -> NoReturn:
            ...         while True:
            ...             # Replenishment logic here
            ...
            >>> limiter = MyRateLimiter(100, 200)
        """
        pass
    
    @abstractmethod
    def calculate_num_token(self, payload: Dict[str, Any], api_endpoint: str) -> int:
        """
        Calculates required tokens for a request.

        Subclasses should implement this method to determine the number of tokens needed based
        on the request payload and target endpoint.

        Args:
            payload (Dict[str, Any]): Payload of the request.
            api_endpoint (str): Target API endpoint for the request.

        Returns:
            int: Calculated number of tokens required for the request.

        Example:
            >>> class MyRateLimiter(RateLimiter):
            ...     def calculate_num_token(self, payload: Dict[str, Any], api_endpoint: str) -> int:
            ...         return len(payload.get('data', '')) // 10
            ...
            >>> limiter = MyRateLimiter(100, 200)
            >>> limiter.calculate_num_token({'data': '12345'}, 'api/send')
            0
        """
        pass

class BaseAPIService(ABC):
    """
    Abstract base class for API services requiring asynchronous operations.

    This class provides foundational attributes and methods for error handling,
    logging, rate-limiting, and re-attempting API calls. It is designed to be
    subclassed for concrete implementations of specific API service interactions.

    Attributes:
        api_key (str): The API key used for authenticating with the API service.
        token_encoding_name (str): The encoding for the API token.
        max_attempts (int): The maximum number of retry attempts for API calls.
        status_tracker (StatusTracker): Tracker for API call statuses.
        rate_limiter (RateLimiter): Limiter to control the rate of API calls.
        queue (AsyncQueue): Queue for managing API call tasks.

    Methods:
        call_api: Abstract method to define API call mechanism in subclasses.
        handle_error: Handle errors by logging and saving details to a JSONL file.
        append_to_jsonl: Append data to a file in JSONL format.
        api_endpoint_from_url: Extract the API endpoint from a URL.
        task_id_generator_function: Generate a sequence of unique task IDs.
    """
    
    def __init__(
        self,
        api_key: str,
        token_encoding_name: str,
        max_attempts: int,
        status_tracker: Optional[StatusTracker],
        rate_limiter: RateLimiter,
        queue: Optional[AsyncQueue]
    ) -> None:
        """
        Initializes the BaseAPIService with necessary configuration.

        Args:
            api_key (str): The API key for authentication.
            token_encoding_name (str): Encoding name for the API token.
            max_attempts (int): Maximum number of attempts for an API call.
            status_tracker (Optional[StatusTracker]): Tracker for API call statuses.
            rate_limiter (RateLimiter): Limiter for API call rates.
            queue (Optional[AsyncQueue]): Queue for managing API tasks.

        Example:
            >>> class MyAPIService(BaseAPIService):
            ...     # Implementation details here
            ...
            >>> service = MyAPIService(api_key="12345", token_encoding_name="utf-8",
            ...                       max_attempts=3, status_tracker=None,
            ...                       rate_limiter=my_rate_limiter, queue=None)
        """
        self.api_key = api_key
        self.token_encoding_name = token_encoding_name
        self.max_attempts = max_attempts
        self.status_tracker = status_tracker or StatusTracker()
        self.rate_limiter = rate_limiter
        self.queue = queue or AsyncQueue()
        
    @abstractmethod
    async def call_api(self) -> Any:
        """
        Abstract method to be implemented for making specific API calls.

        This method should define the logic for interacting with an API endpoint
        and must be implemented in subclasses.

        Example:
            >>> class MyAPIService(BaseAPIService):
            ...     async def call_api(self):
            ...         # Implementation details here
            ...
        """
        pass

    def handle_error(
        self,
        error: Exception,
        payload: Any,
        metadata: Any,
        save_filepath: str
    ) -> None:
        """
        Handles exceptions that occur during the API call process.
        
        Updates the status tracker to indicate the error and saves details to a JSONL file.
        
        Args:
            error (Exception): The exception that was raised during the API call.
            payload (Any): The data payload that was used for the API call.
            metadata (Any): Additional metadata related to the API call.
            save_filepath (str): The file path where error details should be saved.
        """
        self.status_tracker.num_tasks_in_progress -= 1
        self.status_tracker.num_tasks_failed += 1
        data = (
            [payload, [str(error)], metadata] 
            if metadata 
            else [payload, [str(error)]]
        )
        self.append_to_jsonl(data, save_filepath)
        logging.error(f"Request failed after all attempts. Saving errors: {data}")

    @staticmethod
    def append_to_jsonl(data: Any, filename: str) -> None:
        """
        Appends the given data to the specified JSONL file.
        
        Args:
            data (Any): The data to be appended in JSON Lines format.
            filename (str): The file path to the JSONL file.
        """
        json_string = json.dumps(data)
        with open(filename, "a") as f:
            f.write(json_string + "\n")

    @staticmethod
    def api_endpoint_from_url(request_url: str) -> str:
        """
        Extracts the endpoint from an API request URL.
        
        Args:
            request_url (str): The URL from which to extract the API endpoint.
        
        Returns:
            str: The extracted API endpoint.

        Example:
            >>> BaseAPIService.api_endpoint_from_url("https://api.example.com/v1/test_endpoint")
            'test_endpoint'
        """
        match = re.search(r"^https://[^/]+/v\d+/(.+)$", request_url)
        if match:
            return match.group(1)
        else:
            return ""

    @staticmethod
    def task_id_generator_function() -> Generator[int, None, None]:
        """
        Generates a continuous sequence of integers for task IDs.
        
        Yields:
            int: The next task ID in the sequence (0, 1, 2, ...).

        Example:
            >>> id_gen = BaseAPIService.task_id_generator_function()
            >>> next(id_gen)
            0
            >>> next(id_gen)
            1
        """
        task_id = 0
        while True:
            yield task_id
            task_id += 1

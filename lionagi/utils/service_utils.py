import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, NoReturn, Union, List, Optional
import tiktoken

# should be fine ------------------------------------------------------------------
@dataclass
class StatusTracker:
    """
    Class for keeping track of various task statuses.
    
    This class serves as a simple way to monitor different types of task
    outcomes and errors within a system. It uses dataclasses for easy
    creation and management of state.
    
    Attributes:
        num_tasks_started:
            The number of tasks that have been initiated.
        num_tasks_in_progress:
            The number of tasks currently being processed.
        num_tasks_succeeded:
            The number of tasks that have completed successfully.
        num_tasks_failed:
            The number of tasks that have failed.
        num_rate_limit_errors:
            The number of tasks that failed due to rate limiting.
        num_api_errors:
            The number of tasks that failed due to API errors.
        num_other_errors:
            The number of tasks that failed due to other errors.
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
        queue (asyncio.Queue):
            A queue to hold items for asynchronous processing.
        _stop_event (asyncio.Event):
            An event to signal when the queue should stop processing.

    Methods:
        enqueue(item):
            Add an item to the queue for processing.
        dequeue():
            Remove and return an item from the queue.
        join():
            Wait until all items in the queue have been processed.
        stop():
            Signal to stop processing new items in the queue.
        stopped():
            Check if the queue has been signaled to stop.
        process_requests(func):
            Process items using a provided function.
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

        Parameters:
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

        Parameters:
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


class BaseService(ABC):
    
    @abstractmethod
    def __init__(self) -> None:
        ...



class RateLimiter(ABC):
    """
    An abstract base class for rate limiting mechanisms.

    This class defines a structure for rate limiters, which are used to control the frequency
    of requests sent to or received from a network interface controller or an API.

    Attributes:
        max_requests_per_interval (int):
            Maximum number of requests permitted per minute.
        max_tokens_per_interval (int):
            Maximum number of tokens that can accumulate per minute.
        available_request_capacity (int):
            Current number of available request slots.
        available_token_capacity (int):
            Current number of available tokens.

    Methods:
        rate_limit_replenisher:
            Coroutine to replenish rate limits over time.
        calculate_num_token:
            Method to calculate required tokens for a request.
    """
    
    def __init__(self, max_requests_per_interval: int, max_tokens_per_interval: int, interval: int) -> None:
        """
        Initializes the RateLimiter with specified maximum request and token limits.

        Parameters:
            max_requests_per_interval (int): Maximum requests allowed per minute.

            max_tokens_per_interval (int): Maximum tokens allowed to accumulate per minute.
        """
        self.max_requests_per_interval = max_requests_per_interval
        self.max_tokens_per_interval = max_tokens_per_interval
        self.available_request_capacity = max_requests_per_interval
        self.available_token_capacity = max_tokens_per_interval
    
    @abstractmethod
    async def rate_limit_replenisher(self) -> NoReturn:        
        ...


class PayloadMaker:
    def __init__(self, input_: Union[str, List[str]], schema: Dict[str, Any], encoding_name: str) -> None:
        self.input_ = input_
        self.schema = schema
        self.encoding = tiktoken.get_encoding(encoding_name)

    def _create_payload(self, input_: Optional[Union[str, List[str]]] = None,
                       schema: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        input_ = self.input_ if input_ is None else input_
        schema = self.schema if schema is None else schema
        config = {**schema.get('config', {}), **kwargs}
        payload = {schema["input"]: input_}

        for key in schema.get('required', []):
            payload[key] = config[key]

        for key in schema.get('optional', []):
            if key in config and config[key] not in [False, None, "None", "none"]:
                payload[key] = config[key]

        return payload

    def _calculate_num_tokens(self, endpoint_: str) -> int:
        method_name = f"_calculate_token_{endpoint_.replace('/', '_').replace('-', '_')}"
        method = getattr(self, method_name, None)
        if method is None:
            raise NotImplementedError(f'API endpoint "{endpoint_}" not implemented.')
        return method()

    def _calculate_tokens_for_encoded_input(self, input_: Union[str, List[str], bytes]) -> int:
        if isinstance(input_, (str, bytes)):
            return len(self.encoding.encode(input_))
        elif isinstance(input_, list) and all(isinstance(i, str) for i in input_):
            return sum(len(self.encoding.encode(i)) for i in input_)
        else:
            raise TypeError('Input must be a string, bytes, or list of strings.')

    def _calculate_token_chat_completions(self) -> int:
        payload = self.create_payload()
        max_tokens = payload.get("max_tokens", 15)
        n = payload.get("n", 1)
        completion_tokens = max_tokens * n
        num_tokens = sum(4 + sum(len(self.encoding.encode(value)) for key, value in message.items()) -
                         (1 if "name" in message else 0) for message in payload["messages"])
        return num_tokens + 2 + completion_tokens

    def _calculate_token_completions(self) -> int:
        payload = self.create_payload()
        max_tokens = payload.get("max_tokens", 15)
        n = payload.get("n", 1)
        return self._calculate_tokens_for_encoded_input(payload["prompt"]) + max_tokens * n

    def _calculate_token_embeddings(self) -> int:
        payload = self.create_payload()
        return self._calculate_tokens_for_encoded_input(payload["input"])

    def _calculate_token_audio(self) -> int:
        return self._calculate_tokens_for_file_field("audio_file", self.create_payload())

    def _calculate_token_images(self) -> int:
        return self._calculate_tokens_for_file_field("image_file", self.create_payload())

    def _calculate_token_fine_tuning(self) -> int:
        return self._calculate_tokens_for_file_field("training_data", self.create_payload())

    def _calculate_tokens_for_file_field(self, field_name: str, payload: Dict[str, Any]) -> int:
        file_data = payload.get(field_name)
        if isinstance(file_data, str):
            with open(file_data, 'rb') as f:
                file_data = f.read()
        elif not isinstance(file_data, bytes):
            raise TypeError(f'The "{field_name}" field must be a file path or bytes.')
        return len(self.encoding.encode(file_data))
    
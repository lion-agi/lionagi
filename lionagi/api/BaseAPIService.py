import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Optional, Any

from .StatusTracker import StatusTracker
from .AsyncQueue import AsyncQueue
from .RateLimiter import RateLimiter


class BaseAPIService(ABC):
    """
    Abstract base class for an API service.
    
    This class is meant to be subclassed by specific services that implement the
    `call_api_endpoint` method. It provides common functionality for handling errors,
    appending data to a JSONL file, and extracting the API endpoint from a URL.
    
    Attributes:
        api_key: API key for authentication with the service.
        token_encoding_name: Name of the token encoding used.
        max_attempts: Maximum number of attempts for a single API call.
        status_tracker: StatusTracker for keeping track of API call outcomes.
        rate_limiter: RateLimiter to control the rate of API calls.
        queue: AsyncQueue to manage asynchronous tasks.
    """
    
    def __init__(self, api_key: str, token_encoding_name: str, max_attempts: int,
                 status_tracker: Optional[StatusTracker], rate_limiter: RateLimiter,
                 queue: Optional[AsyncQueue]) -> None:
        """
        Initialize a BaseAPIService with the given parameters.
        
        Args:
            api_key: API key for service authentication.
            token_encoding_name: Encoding name for the API token.
            max_attempts: Maximum number of call attempts.
            status_tracker: Optional StatusTracker instance.
            rate_limiter: RateLimiter to control call rate.
            queue: Optional AsyncQueue instance for asynchronous task management.
        """

        self.api_key = api_key
        self.token_encoding_name = token_encoding_name
        self.max_attempts = max_attempts
        self.status_tracker = status_tracker or StatusTracker()
        self.rate_limiter = rate_limiter
        self.queue = queue or AsyncQueue()
        
    @abstractmethod
    async def call_api_endpoint(self) -> Any:
        """Abstract method to call the API endpoint. Must be implemented by subclasses."""
        pass

    def handle_error(self, error: Exception, payload: Any, metadata: Any,
                     save_filepath: str) -> None:
        """
        Handle errors encountered during API calls by logging and saving them.
        
        Decrements the 'in progress' counter and increments the 'failed' counter
        on the status tracker. Appends error details to a JSONL file.
        
        Args:
            error: The error that occurred.
            payload: The payload involved in the request causing the error.
            metadata: Additional metadata associated with the request.
            save_filepath: Path to the file where details should be saved.
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
        Append data to a JSONL (JSON Lines) file.
        
        Args:
            data: The data to be serialized to JSON and written to the file.
            filename: The filename of the JSONL file to append to.
        """  
        json_string = json.dumps(data)
        with open(filename, "a") as f:
            f.write(json_string + "\n")

    @staticmethod
    def api_endpoint_from_url(request_url: str) -> str:
        """
        Extract the API endpoint from the request URL.
        
        Args:
            request_url: The full URL of the API request.
        
        Returns:
            The extracted API endpoint from the URL.
        """
        match = re.search("^https://[^/]+/v\\d+/(.+)$", request_url)
        return match[1]
    
    @staticmethod
    def task_id_generator_function() -> Any:
        """
        Generate a continuous sequence of integers (0, 1, 2, ...).
        
        Yields:
            A sequence of integers, starting from 0 and incrementing by 1 each time.
        """
        task_id = 0
        while True:
            yield task_id
            task_id += 1

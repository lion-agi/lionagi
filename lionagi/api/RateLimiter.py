from abc import ABC, abstractmethod
import asyncio
from typing import NoReturn

class RateLimiter(ABC):
    """
    An abstract base class to define the structure of a rate limiter.

    Attributes:
        max_requests_per_minute (int): The maximum number of requests allowed per minute.
        max_tokens_per_minute (int): The maximum number of tokens allowed per minute.
        available_request_capacity (int): The current available request capacity.
        available_token_capacity (int): The current available token capacity.
        rate_limit_replenisher_task (asyncio.Task): The background task to replenish rate limits.

    Methods:
        rate_limit_replenisher: The coroutine that replenishes the rate limits.
        calculate_num_token: A method to calculate the number of tokens needed.
    """
    
    def __init__(self, max_requests_per_minute: int, max_tokens_per_minute: int):
        """
        Initialize the RateLimiter with the specified capacities.

        Args:
            max_requests_per_minute (int): The maximum number of requests per minute.
            max_tokens_per_minute (int): The maximum number of tokens per minute.
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_minute = max_tokens_per_minute
        self.available_request_capacity = max_requests_per_minute
        self.available_token_capacity = max_tokens_per_minute
        self.rate_limit_replenisher_task = asyncio.create_task(self.rate_limit_replenisher())

    @abstractmethod
    async def rate_limit_replenisher(self) -> NoReturn:
        """
        Asynchronously replenish the rate limits.
        
        This coroutine should implement the logic to replenish the available_request_capacity
        and the available_token_capacity at regular intervals.
        """
        pass
    
    @abstractmethod
    def calculate_num_token(self, payload: dict, api_endpoint: str, token_encoding_name: str) -> int:
        """
        Calculate the number of tokens needed based on some criteria.

        Returns:
            int: The calculated number of tokens.
        """
        pass
    
from os import getenv
import asyncio
from typing import NoReturn
from lionagi.objs.service_utils import RateLimiter

class BaseRateLimiter(RateLimiter):
    """
    BaseRateLimiter extends the RateLimiter class to implement specific rate limiting logic.

    This class provides functionality to manage the rate of requests sent to a network interface
    or API by controlling the number of requests and tokens within a given time interval.

    Attributes:
    
        interval (int): The time interval in seconds for replenishing the rate limit capacity.
        
        rate_limit_replenisher_task (asyncio.Task): An asyncio task that runs the rate limit replenisher coroutine.

    Methods:
    
        create: Class method to initialize and start the rate limit replenisher task.
        
        rate_limit_replenisher: Coroutine that replenishes rate limits at set intervals.
        
        _is_busy: Checks if the rate limiter is currently busy.
        
        _has_capacity: Checks if there is enough capacity for a request.
        
        _reduce_capacity: Reduces the available capacities by the required tokens.
    """

    def __init__(
        self, 
        max_requests_per_interval: int, 
        max_tokens_per_interval: int,
        interval: int = 60,
    ) -> None:
        """
        Initializes the BaseRateLimiter with specific rate limits and interval.

        Parameters:
        
            max_requests_per_interval (int): Maximum number of requests allowed per interval.
            
            max_tokens_per_interval (int): Maximum number of tokens that can be used per interval.
            
            interval (int): The time interval in seconds for replenishing rate limits. Defaults to 60 seconds.
        """
        
        super().__init__(max_requests_per_interval, max_tokens_per_interval)
        self.interval = interval
        self.rate_limit_replenisher_task = asyncio.create_task(
            self.rate_limit_replenisher.create(max_requests_per_interval, 
                                               max_tokens_per_interval))

    @classmethod
    async def create(
        cls, max_requests_per_interval: int, max_tokens_per_interval: int
    ) -> None:
        """
        Class method to initialize and start the rate limit replenisher task.

        Parameters:
            max_requests_per_interval (int): Maximum number of requests allowed per interval.
            max_tokens_per_interval (int): Maximum number of tokens that can be used per interval.

        Returns:
            An instance of BaseRateLimiter with the replenisher task running.

        Note:
            If the environment variable "env_readthedocs" is set, the replenisher task is not started.
        """
        self = cls(max_requests_per_interval, max_tokens_per_interval)
        if not getenv.getenv("env_readthedocs"):
            self.rate_limit_replenisher_task = await asyncio.create_task(
                self.rate_limit_replenisher()
            )
        return self

    async def rate_limit_replenisher(self) -> NoReturn:
        """
        A coroutine that replenishes rate limits at set intervals.

        This coroutine runs in a loop, sleeping for the specified interval and then replenishing
        the request and token capacities to their maximum values.
        """
        while True:
            await asyncio.sleep(self.interval)  # Replenishes every interval seconds
            self.available_request_capacity = self.max_requests_per_interval
            self.available_token_capacity = self.max_tokens_per_interval
    
    def _is_busy(self) -> bool:
        """
        Checks if the rate limiter is currently busy.

        Returns:
            bool: True if the available request capacity is less than 1 or the available token capacity is less than 10.
        """
        return self.available_request_capacity < 1 or self.available_token_capacity < 10
    
    def _has_capacity(self, required_tokens: int) -> bool:
        """
        Checks if there is enough capacity for a request based on required tokens.

        Parameters:
            required_tokens (int): The number of tokens required for the request.

        Returns:
            bool: True if the available token capacity is greater than or equal to the required tokens.
        """
        return self.available_token_capacity >= required_tokens
    
    def _reduce_capacity(self, required_tokens: int) -> None:
        """
        Reduces the available capacities by the required tokens.

        Parameters:
            required_tokens (int): The number of tokens to reduce from the available capacity.
        """
        self.available_request_capacity -= 1
        self.available_token_capacity -= required_tokens
        
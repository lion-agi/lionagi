from abc import ABC, abstractmethod

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
        self.interval=interval
    
    @abstractmethod
    async def rate_limit_replenisher(self):        
        ...

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
        
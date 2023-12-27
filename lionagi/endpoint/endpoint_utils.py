from abc import ABC, abstractmethod

class RateLimiter(ABC):
    """
    An abstract base class for rate limiting mechanisms.

    This class defines a structure for rate limiters, which are used to control the frequency
    of requests sent to or received from a network interface controller or an API.

    Attributes:
        max_requests_per_minute (int):
            Maximum number of requests permitted per minute.
        max_tokens_per_minute (int):
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
    @abstractmethod
    def __init__(self) -> None:
        ...
        
    @abstractmethod
    async def rate_limit_replenisher(self) -> NoReturn:
        ...
    
    @abstractmethod
    def calculate_num_token(self, payload: Dict[str, Any], api_endpoint: str) -> int:
        ...
from abc import abstractmethod, ABC, abstractproperty
from typing import Any, Dict, NoReturn


class BaseService(ABC):
    
    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    async def serve(self) -> Any:     
        ...
        
        
class RateLimiter(ABC):

    def __init__(self, max_requests_per_minute: int, max_tokens_per_minute: int) -> None:
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_minute = max_tokens_per_minute
        self.available_request_capacity = max_requests_per_minute
        self.available_token_capacity = max_tokens_per_minute
    
    @abstractmethod
    async def rate_limit_replenisher(self) -> NoReturn:
        ...
    
    @abstractmethod
    def calculate_num_token(self, payload: Dict[str, Any], api_endpoint: str) -> int:
        ...
        

class BaseEndpoint(ABC):
    
    endpoint: str = abstractproperty()

    @abstractmethod
    def create_payload(self, **kwargs):
        ...

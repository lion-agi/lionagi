import asyncio
import logging
import aiohttp
from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, NoReturn, Optional, Type, List, Union

from ..utils import nget, APIUtil


@dataclass
class StatusTracker:
    """
    Keeps track of various task statuses within a system.

    Attributes:
        num_tasks_started (int): The number of tasks that have been initiated.
        num_tasks_in_progress (int): The number of tasks currently being processed.
        num_tasks_succeeded (int): The number of tasks that have completed successfully.
        num_tasks_failed (int): The number of tasks that have failed.
        num_rate_limit_errors (int): The number of tasks that failed due to rate limiting.
        num_api_errors (int): The number of tasks that failed due to API errors.
        num_other_errors (int): The number of tasks that failed due to other errors.

    Examples:
        >>> tracker = StatusTracker()
        >>> tracker.num_tasks_started += 1
        >>> tracker.num_tasks_succeeded += 1
    """
    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_rate_limit_errors: int = 0
    num_api_errors: int = 0
    num_other_errors: int = 0


class BaseRateLimiter(ABC):
    """
    Abstract base class for implementing rate limiters.

    This class provides the basic structure for rate limiters, including
    the replenishment of request and token capacities at regular intervals.

    Attributes:
        interval (int): The time interval in seconds for replenishing capacities.
        max_requests (int): The maximum number of requests allowed per interval.
        max_tokens (int): The maximum number of tokens allowed per interval.
        available_request_capacity (int): The current available request capacity.
        available_token_capacity (int): The current available token capacity.
        rate_limit_replenisher_task (Optional[asyncio.Task[NoReturn]]): The asyncio task for replenishing capacities.

    Examples:
        # Example usage of a derived class implementing BaseRateLimiter
        class MyRateLimiter(BaseRateLimiter):
            async def request_permission(self) -> bool:
                # Implementation for requesting permission to make an API call
                pass

        rate_limiter = MyRateLimiter(max_requests=10, max_tokens=100, interval=60)
        asyncio.run(rate_limiter.start_replenishing())
    """

    def __init__(self, max_requests: int, max_tokens: int, interval: int = 60, token_encoding_name=None) -> None:
        self.interval: int = interval
        self.max_requests: int = max_requests
        self.max_tokens: int = max_tokens
        self.available_request_capacity: int = max_requests
        self.available_token_capacity: int = max_tokens
        self.rate_limit_replenisher_task: Optional[asyncio.Task[NoReturn]] = None
        self._stop_replenishing: asyncio.Event = asyncio.Event()
        self._lock: asyncio.Lock = asyncio.Lock()
        self.token_encoding_name = token_encoding_name

    async def start_replenishing(self) -> NoReturn:
        """Starts the replenishment of rate limit capacities at regular intervals."""
        try:
            while not self._stop_replenishing.is_set():
                await asyncio.sleep(self.interval)
                async with self._lock:
                    self.available_request_capacity = self.max_requests
                    self.available_token_capacity = self.max_tokens
        except asyncio.CancelledError:
            logging.info("Rate limit replenisher task cancelled.")
        except Exception as e:
            logging.error(f"An error occurred in the rate limit replenisher: {e}")

    async def stop_replenishing(self) -> None:
        """Stops the replenishment task."""
        if self.rate_limit_replenisher_task:
            self.rate_limit_replenisher_task.cancel()
            await self.rate_limit_replenisher_task
        self._stop_replenishing.set()

    async def request_permission(self, required_tokens) -> bool:
        """Requests permission to make an API call.

        Returns True if the request can be made immediately, otherwise False.
        """
        async with self._lock:
            if self.available_request_capacity > 0 and self.available_token_capacity > 0:
                self.available_request_capacity -= 1
                self.available_token_capacity -= required_tokens  # Assuming 1 token per request for simplicity
                return True
            return False

    async def _call_api(
        self, 
        http_session, 
        endpoint, 
        base_url, 
        api_key,
        max_attempts=3, 
        method="post", 
        payload: Dict[str, any]=None
    ) -> Optional[Dict[str, any]]:
        endpoint = APIUtil.api_endpoint_from_url(base_url + endpoint)
        while True:
            if self.available_request_capacity < 1 or self.available_token_capacity < 10:  # Minimum token count
                await asyncio.sleep(1)  # Wait for capacity
                continue
            required_tokens = APIUtil.calculate_num_token(payload, endpoint, self.token_encoding_name)
            
            if await self.request_permission(required_tokens):
                request_headers = {"Authorization": f"Bearer {api_key}"}
                attempts_left = max_attempts

                while attempts_left > 0:
                    try:
                        method = APIUtil.api_method(http_session, method)                         
                        async with method(
                            url=(base_url+endpoint), headers=request_headers, json=payload
                        ) as response:
                            response_json = await response.json()

                            if "error" in response_json:
                                logging.warning(
                                    f"API call failed with error: {response_json['error']}"
                                )
                                attempts_left -= 1

                                if "Rate limit" in response_json["error"].get("message", ""):
                                    await asyncio.sleep(15)
                            else:
                                return response_json
                    except Exception as e:
                        logging.warning(f"API call failed with exception: {e}")
                        attempts_left -= 1

                logging.error("API call failed after all attempts.")
                break
            else:
                await asyncio.sleep(1)

    @classmethod
    async def create(cls, max_requests: int, max_tokens: int, interval: int = 60, token_encoding_name = None) -> 'BaseRateLimiter':
        """Creates an instance of BaseRateLimiter and starts the replenisher task."""
        instance = cls(max_requests, max_tokens, interval, token_encoding_name)
        instance.rate_limit_replenisher_task = asyncio.create_task(
            instance.start_replenishing()
        )
        return instance


class SimpleRateLimiter(BaseRateLimiter):
    """
    A simple implementation of a rate limiter.

    Inherits from BaseRateLimiter and provides a basic rate limiting mechanism.

    Examples:
        # Example usage of SimpleRateLimiter
        rate_limiter = SimpleRateLimiter(max_requests=10, max_tokens=100, interval=60)
        asyncio.run(rate_limiter.start_replenishing())
    """

    def __init__(self, max_requests: int, max_tokens: int, interval: int = 60, token_encoding_name=None) -> None:
        super().__init__(max_requests, max_tokens, interval, token_encoding_name)


class EndPoint:
    """
    Represents an API endpoint with rate limiting capabilities.

    This class encapsulates the details of an API endpoint, including its rate limiter.

    Attributes:
        endpoint (str): The API endpoint path.
        rate_limiter_class (Type[li.BaseRateLimiter]): The class used for rate limiting requests to the endpoint.
        max_requests (int): The maximum number of requests allowed per interval.
        max_tokens (int): The maximum number of tokens allowed per interval.
        interval (int): The time interval in seconds for replenishing rate limit capacities.
        config (Dict): Configuration parameters for the endpoint.
        rate_limiter (Optional[li.BaseRateLimiter]): The rate limiter instance for this endpoint.

    Examples:
        # Example usage of EndPoint with SimpleRateLimiter
        endpoint = EndPoint(
            max_requests=100,
            max_tokens=1000,
            interval=60,
            endpoint_='chat/completions',
            rate_limiter_class=li.SimpleRateLimiter,
            config={'param1': 'value1'}
        )
        asyncio.run(endpoint.init_rate_limiter())
    """

    def __init__(
        self,
        max_requests: int = 1000,
        max_tokens: int = 100000,
        interval: int = 60,
        endpoint_: Optional[str] = None,
        rate_limiter_class: Type[BaseRateLimiter] = SimpleRateLimiter,
        token_encoding_name=None,
        config: Dict = None,
    ) -> None:
        self.endpoint = endpoint_ or 'chat/completions'
        self.rate_limiter_class = rate_limiter_class
        self.max_requests = max_requests
        self.max_tokens = max_tokens
        self.interval = interval
        self.token_encoding_name = token_encoding_name
        self.config = config or {}
        self.rate_limiter: Optional[BaseRateLimiter] = None
        self._has_initialized = False

    async def init_rate_limiter(self) -> None:
        """Initializes the rate limiter for the endpoint."""
        self.rate_limiter = await self.rate_limiter_class.create(
            self.max_requests, self.max_tokens, self.interval, self.token_encoding_name
        )
        self._has_initialized = True


class BaseService:
    """
    Base class for services that interact with API endpoints.

    This class provides a foundation for services that need to make API calls with rate limiting.

    Attributes:
        api_key (Optional[str]): The API key used for authentication.
        schema (Dict[str, Any]): The schema defining the service's endpoints.
        status_tracker (StatusTracker): The object tracking the status of API calls.
        endpoints (Dict[str, EndPoint]): A dictionary of endpoint objects.

    Examples:
        # Example usage of BaseService with OpenAIService
        service = OpenAIService(api_key='your_api_key')
        asyncio.run(service.init_endpoints())
        response = asyncio.run(service.serve('data', 'chat/completions'))
    """

    base_url: str = ''
    available_endpoints: list = []

    def __init__(
        self,
        api_key: Optional[str] = None,
        schema: Dict[str, Any] = None,
        token_encoding_name: str = None
    ) -> None:
        self.api_key = api_key
        self.schema = schema or {}
        self.status_tracker = StatusTracker()
        self.endpoints: Dict[str, EndPoint] = {}
        self.token_encoding_name = token_encoding_name

    async def init_endpoint(self, endpoint_: Optional[Union[List[str], List[EndPoint], str, EndPoint]] = None) -> None:
        """Initializes the specified endpoint or all endpoints if none is specified."""
        
        if endpoint_:
            if not isinstance(endpoint_, list):
                endpoint_ = [endpoint_]
            for ep in endpoint_:
                if ep not in self.available_endpoints:
                    raise ValueError (f"Endpoint {ep} not available for service {self.__class__.__name__}")

                if ep not in self.endpoints:
                    endpoint_config = nget(self.schema, [ep, 'config'])
                    self.schema.get(ep, {})
                    if isinstance(ep, EndPoint):
                        self.endpoints[ep.endpoint] = ep
                    else:
                        self.endpoints[ep] = EndPoint(
                            max_requests=endpoint_config.get('max_requests', 1000) if endpoint_config.get('max_requests', 1000) is not None else 1000,
                            max_tokens=endpoint_config.get('max_tokens', 100000) if endpoint_config.get('max_tokens', 100000) is not None else 100000,
                            interval=endpoint_config.get('interval', 60) if endpoint_config.get('interval', 60) is not None else 60,
                            endpoint_=ep,
                            token_encoding_name=self.token_encoding_name,
                            config=endpoint_config,
                        )

                if not self.endpoints[ep]._has_initialized:
                    await self.endpoints[ep].init_rate_limiter()

        else:
            for ep in self.available_endpoints:
                endpoint_config = nget(self.schema, [ep, 'config'])
                self.schema.get(ep, {})
                if ep not in self.endpoints:
                    self.endpoints[ep] = EndPoint(
                        max_requests=endpoint_config.get('max_requests', 1000),
                        max_tokens=endpoint_config.get('max_tokens', 100000),
                        interval=endpoint_config.get('interval', 60),
                        endpoint_=ep,
                        token_encoding_name=self.token_encoding_name,
                        config=endpoint_config,
                    )
                if not self.endpoints[ep]._has_initialized:
                    await self.endpoints[ep].init_rate_limiter()

    async def call_api(self, payload, endpoint, method):
        if endpoint not in self.endpoints.keys():
            raise ValueError(f'The endpoint {endpoint} has not initialized.')
        async with aiohttp.ClientSession() as http_session:
            completion = await self.endpoints[endpoint].rate_limiter._call_api(
                http_session=http_session, endpoint=endpoint, base_url=self.base_url, api_key=self.api_key,
                method=method, payload=payload)
            return completion


class PayloadCreation:
    
    @classmethod
    def chat_completion(cls, messages, llmconfig, schema, **kwargs):
        return APIUtil._create_payload(
            input_=messages, 
            config=llmconfig, 
            required_=schema['required'], 
            optional_=schema['optional'],
            input_key="messages", 
            **kwargs)

    @classmethod
    def fine_tuning(cls, training_file, llmconfig, schema, **kwargs):
        return APIUtil._create_payload(
            input_=training_file, 
            config=llmconfig, 
            required_=schema['required'], 
            optional_=schema['optional'],
            input_key="training_file", 
            **kwargs)
        
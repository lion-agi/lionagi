from os import getenv
import asyncio
import aiohttp
import logging

from typing import Dict, Optional, Any, NoReturn
from lionagi.utils.api_util import api_method, api_endpoint_from_url, api_error, api_rate_limit_error
from lionagi.objs import StatusTracker, AsyncQueue, PayloadMaker
from lionagi.services.base_ import BaseService, RateLimiter

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



class BaseAPIService(BaseService):
    """
    BaseAPIService provides a foundational structure for making API calls.

    This class integrates rate limiting, payload creation, and status tracking 
    functionalities to manage API requests efficiently.

    Attributes:
        base_url (str): The base URL for the API endpoints.
        _api_key (str): The API key used for authorization in API calls.
        max_attempts (int): Maximum number of retry attempts for an API call.
        payload_maker (PayloadMaker): An instance of PayloadMaker for creating 
        API request payloads.
        status_tracker (StatusTracker): Tracks the status of API requests.
        queue (AsyncQueue): Manages asynchronous tasks.
        rate_limiter (BaseRateLimiter): Implements rate limiting for API calls.

    Methods:
        create_payload: Generates a payload for an API request based on given 
        input and schema.
        
        calculate_num_tokens: Calculates the number of tokens required for a 
        specific API endpoint.
        
        is_busy: Checks if the rate limiter is currently busy.
        
        has_capacity: Checks if there is enough capacity for a request based 
        on required tokens.
        
        reduce_capacity: Reduces the available capacity of the rate limiter 
        by the required tokens.
        
        get_api_response: Sends an API request and retrieves the response.
        
        _base_call_api: Manages the entire process of making an API call including 
        handling retries and rate limiting.
        
        _serve: Serves as the primary method to initiate and handle an API call.
    """
     
    base_url = ''
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        ratelimiter: Optional[BaseRateLimiter] = BaseRateLimiter,
        max_requests_per_interval: Optional[int] = None,
        max_tokens_per_interval: Optional[int] = None,
        interval: int = 60,
        max_attempts: int = 3
        ) -> None:
        """
        Initializes the BaseAPIService with necessary configurations and instances.

        Parameters:
            api_key (Optional[str]): The API key used for authorization.
            
            ratelimiter (BaseRateLimiter): The rate limiting mechanism to be used.
            
            max_requests_per_interval (Optional[int]): Maximum number of requests per interval.
            
            max_tokens_per_interval (Optional[int]): Maximum number of tokens per interval.
            
            interval (int): The time interval in seconds for the rate limiter.
            
            max_attempts (int): Maximum number of attempts for an API call.
        """   
        self._api_key = api_key
        self.max_attempts = max_attempts
        
        self.payload_maker = PayloadMaker()
        self.status_tracker = StatusTracker()
        self.queue = AsyncQueue()
        self.rate_limiter = ratelimiter(
            max_requests_per_interval=max_requests_per_interval, 
            max_tokens_per_interval=max_tokens_per_interval, 
            interval=interval)

    def create_payload(self, input_, schema, **kwargs):
        return self.payload_maker._create_payload(
            input_=input_, schema=schema, **kwargs)

    def calculate_num_tokens(self, input_, endpoint_, encoding_name):
        self.payload_maker.input_ = input_
        self.payload_maker.encoding_name = encoding_name
        return self.payload_maker._calculate_num_tokens(endpoint_=endpoint_)
    
    def is_busy(self):
        return self.rate_limiter._is_busy()
    
    def has_capacity(self, required_tokens):
        return self.rate_limiter._has_capacity(required_tokens)
    
    def reduce_capacity(self, required_tokens):
        self.rate_limiter._reduce_capacity(required_tokens)
    
    async def get_api_response(self, 
                               http_session, 
                               request_headers, 
                               method, 
                               payload, 
                               endpoint_, 
                               base_url
                               ):
        method = api_method(
            http_session=http_session, 
            method=method
        )
        base_url = base_url or self.base_url
        async with method(
            url = (base_url + endpoint_),
            headers=request_headers, json=payload
            ) as response:
            return await response.json()
        
    # kwargs for create payload
    async def _base_call_api(self,
                             http_session,
                             input_=None,
                             schema=None, 
                             endpoint_=None, 
                             method="post", 
                             payload: Dict[str, any] =None,
                             encoding_name: str = None,
                             **kwargs) -> Optional[Dict[str, any]]:
        
        endpoint_ = api_endpoint_from_url(self.base_url + endpoint_)
        payload = payload or self.create_payload(input_=input_,
                                                 schema=schema, 
                                                 **kwargs)
        if encoding_name:
            self.payload_maker.encoding_name = encoding_name

        while True:
            if self.is_busy():
                await asyncio.sleep(1)
                
            required_tokens = self.calculate_num_tokens(input_=input_, endpoint_=endpoint_)

            if self.has_capacity(required_tokens):
                self.reduce_capacity(required_tokens)

                request_headers = {"Authorization": f"Bearer {self._api_key}"}
                attempts_left = self.max_attempts

                while attempts_left > 0:
                    try:
                        response_json = await self.get_api_response(
                            http_session=http_session,
                            request_headers=request_headers,
                            method=method,
                            payload=payload,
                            endpoint_=endpoint_,
                            base_url=self.base_url)
                                                
                        if api_error(response_json=response_json):
                            attempts_left -= 1     
                            if api_rate_limit_error(response_json=response_json):
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
    
    async def _serve(self,
                     input_: Optional[Any] = None,
                     schema: Optional[Dict[str, Any]] = None, 
                     endpoint_: Optional[str] = None, 
                     method: str = "post", 
                     payload: Optional[Dict[str, Any]] = None,
                     encoding_name: Optional[str] = None,
                     **kwargs) -> Optional[Any]:
        """
        Initiates and manages an API call process.

        This method creates an HTTP session, makes the API call, handles retries, and tracks the
        status of the request.

        Parameters:
            input_ (Optional[Any]): The input for creating the payload.
            
            schema (Optional[Dict[str, Any]]): The schema to be used for payload creation.
            
            endpoint_ (Optional[str]): The endpoint for the API call.
            
            method (str): The HTTP method to be used. Defaults to 'post'.
            
            payload (Optional[Dict[str, Any]]): The payload for the API request.
            
            encoding_name (Optional[str]): The encoding to be used for token calculations.
            
            **kwargs: Additional keyword arguments for payload creation.

        Returns:
            Optional[Any]: The response from the API call, or None if an error occurs.

        Raises:
            Exception: Captures and logs any exceptions during the API call process.
        """
        try:
            async with aiohttp.ClientSession() as http_session:    
                completion = await self._base_call_api(
                    http_session=http_session,
                    schema=schema,
                    input_=input_,
                    endpoint_=endpoint_,
                    method=method,
                    payload=payload,
                    encoding_name=encoding_name,
                    **kwargs)
                return completion
            
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e
        
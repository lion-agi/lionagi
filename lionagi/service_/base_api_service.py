import asyncio
import aiohttp
import logging

from os import getenv
from typing import Dict, Optional, Any

from lionagi.utils.api_util import api_methods, api_endpoint_from_url, api_error, rate_limit_error
from lionagi.objs.service_utils import BaseService, StatusTracker, AsyncQueue, PayloadMaker
from .base_rate_limiter import BaseRateLimiter


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
        method = api_methods(
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
                            if rate_limit_error(response_json=response_json):
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
        
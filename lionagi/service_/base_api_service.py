import asyncio
import aiohttp
import logging

from os import getenv
from typing import Dict, Optional

from ..utils.api_utils import api_methods, api_endpoint_from_url, api_error, rate_limit_error
from ..utils.service_utils import BaseService, StatusTracker, AsyncQueue, PayloadMaker
from .base_rate_limiter import BaseRateLimiter


class BaseAPIService(BaseService):
    base_url = ''
    
    def __init__(
        self, 
        api_key: str = None, 
        ratelimiter = BaseRateLimiter,
        max_requests_per_interval=None,
        max_tokens_per_interval=None,
        interval=60,
        max_attempts = 3
        ) -> None:
        
        self._api_key = api_key
        self.max_attempts = max_attempts
        self.payload_manager = PayloadMaker()
        self.status_tracker = StatusTracker()
        self.queue = AsyncQueue()
        self.rate_limiter = ratelimiter(
            max_requests_per_interval=max_requests_per_interval, 
            max_tokens_per_interval=max_tokens_per_interval, 
            interval=interval)

    def create_payload(self, input_, schema, **kwargs):
        return self.payload_manager._create_payload(
            input_=input_, schema=schema, **kwargs)

    def calculate_num_tokens(self, input_, endpoint_, encoding_name):
        self.payload_manager.input_ = input_
        self.payload_manager.encoding_name = encoding_name
        return self.payload_manager._calculate_num_tokens(endpoint_=endpoint_)
    
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
            self.payload_manager.encoding_name = encoding_name

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
                       input_=None,
                       schema=None, 
                       endpoint_=None, 
                       method="post", 
                       payload: Dict[str, any] =None,
                       encoding_name: str = None,
                       **kwargs):
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
        
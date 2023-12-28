import os
import dotenv
import asyncio
import logging
import aiohttp
from typing import Optional
from .base_service import BaseAPIService, BaseAPIRateLimiter

dotenv.load_dotenv()

from .base_service import BaseAPIService



class OpenAIService(BaseAPIService):
    """
    Service class for interacting with the OpenAI API.

    This class provides methods for calling OpenAI's API endpoints, handling the responses,
    and managing rate limits and asynchronous tasks associated with API calls.

    Attributes:
        base_url (str): The base URL for OpenAI's API.

    Methods:
        call_api: Call an API endpoint with a payload and handle the response.
    """

    base_url = "https://api.openai.com/v1/"

    def __init__(
        self,
        api_key: str = None,
        token_encoding_name: str = "cl100k_base",
        max_attempts: int = 3,
        max_requests_per_minute: int = 500,
        max_tokens_per_minute: int = 150_000,
        ratelimiter = BaseAPIRateLimiter ,
        status_tracker = None,
        queue = None,
    ):
        super().__init__(
            api_key = api_key or os.getenv("OPENAI_API_KEY"),
            status_tracker = status_tracker,
            queue = queue,
            ratelimiter=ratelimiter,
            max_requests_per_minute=max_requests_per_minute, 
            max_tokens_per_minute=max_tokens_per_minute),
        self.token_encoding_name=token_encoding_name
        self.max_attempts = max_attempts
        
        
    async def _call_api(self, http_session, endpoint_, method="post", payload: Dict[str, any] =None) -> Optional[Dict[str, any]]:
        endpoint_ = self.api_endpoint_from_url(self.base_url+endpoint_)
        
        while True:
            if self.rate_limiter.available_request_capacity < 1 or self.rate_limiter.available_token_capacity < 10:  # Minimum token count
                await asyncio.sleep(1)  # Wait for capacity
                continue
            
            required_tokens = self.rate_limiter.calculate_num_token(payload, endpoint_, self.token_encoding_name)
            
            if self.rate_limiter.available_token_capacity >= required_tokens:
                self.rate_limiter.available_request_capacity -= 1
                self.rate_limiter.available_token_capacity -= required_tokens

                request_headers = {"Authorization": f"Bearer {self.api_key}"}
                attempts_left = self.max_attempts

                while attempts_left > 0:
                    try:
                        method = self.api_methods(http_session, method)                         
                        async with method(
                            url=(self.base_url+endpoint_), headers=request_headers, json=payload
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
    
    async def serve(self, payload, endpoint_="chat/completions", method="post"):
         
        async def call_api():
            async with aiohttp.ClientSession() as http_session:
                completion = await self._call_api(http_session=http_session, endpoint_=endpoint_, payload=payload, method=method)
                return completion

        try:
            return await call_api()
        except Exception as e:
                self.status_tracker.num_tasks_failed += 1
                raise e
        
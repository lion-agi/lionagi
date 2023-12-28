import os
import dotenv
import asyncio
import logging
import tiktoken
import aiohttp
from typing import Optional, NoReturn, Dict, Any

from .base_service import BaseAPIService

dotenv.load_dotenv()

from .service_utils import RateLimiter
from .base_service import BaseAPIService
from .service_utils import StatusTracker, AsyncQueue








class OpenAIRateLimiter(RateLimiter):
    """
    A specialized RateLimiter for managing requests to the OpenAI API.

    Extends the generic RateLimiter to enforce specific rate-limiting rules and limits
    as required by the OpenAI API. This includes maximum requests and tokens per minute
    and replenishing these limits at regular intervals.

    Attributes:
        max_requests_per_minute (int): Maximum number of requests allowed per minute.
        max_tokens_per_minute (int): Maximum number of tokens allowed per minute.

    Methods:
        rate_limit_replenisher: Coroutine to replenish rate limits over time.
        calculate_num_token: Calculates the required tokens for a request.
    """

    def __init__(self, max_requests_per_minute: int = 500, max_tokens_per_minute: int = 150_000) -> None:
        """
        Initializes the rate limiter with specific limits for OpenAI API.

        Args:
            max_requests_per_minute (int): The maximum number of requests allowed per minute.
            max_tokens_per_minute (int): The maximum number of tokens that can accumulate per minute.
        """
        self.max_requests_perminute=max_requests_per_minute
        self.max_tokens_per_minute=max_tokens_per_minute
        if not os.getenv('env_readthedocs'):
            self.rate_limit_replenisher_task = asyncio.create_task(self.rate_limit_replenisher())
    
    async def rate_limit_replenisher(self) -> NoReturn:
        """
        Asynchronously replenishes the rate limit capacities at regular intervals.

        This coroutine runs indefinitely, replenishing the available request and token capacities
        based on the maximum limits defined for the OpenAI API. This task should run in the background
        to consistently reset the capacities.

        Example:
            >>> rate_limiter = OpenAIRateLimiter(100, 200)
            >>> asyncio.create_task(rate_limiter.rate_limit_replenisher())
            # This will start the background task for rate limit replenishment.
        """
        while True:
            await asyncio.sleep(60)  # Replenishes every 60 seconds
            self.available_request_capacity = self.max_requests_per_minute
            self.available_token_capacity = self.max_tokens_per_minute
            
    def calculate_num_token(self, payload: Dict[str, Any] =None, 
                            api_endpoint: str =None, token_encoding_name: str =None) -> int:
        """
        Calculates the number of tokens required for a request based on the payload and API endpoint.

        The token calculation logic might vary based on different API endpoints and payload content.
        This method should be implemented in a subclass to provide the specific calculation logic
        for the OpenAI API.

        Args:
            payload (Dict[str, Any]): The payload of the request.
            api_endpoint (str): The specific API endpoint for the request.

        Returns:
            int: The estimated number of tokens required for the request.

        Example:
            >>> rate_limiter = OpenAIRateLimiter(100, 200)
            >>> payload = {'prompt': 'Translate the following text:', 'max_tokens': 50}
            >>> rate_limiter.calculate_num_token(payload, 'completions')
            # Expected token calculation for the given payload and endpoint.
        """

        encoding = tiktoken.get_encoding(token_encoding_name)
        if api_endpoint.endswith("completions"):
            max_tokens = payload.get("max_tokens", 15)
            n = payload.get("n", 1)
            completion_tokens = n * max_tokens

            # chat completions
            if api_endpoint.startswith("chat/"):
                num_tokens = 0
                for message in payload["messages"]:
                    num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                    for key, value in message.items():
                        num_tokens += len(encoding.encode(value))
                        if key == "name":  # if there's a name, the role is omitted
                            num_tokens -= 1  # role is always required and always 1 token
                num_tokens += 2  # every reply is primed with <im_start>assistant
                return num_tokens + completion_tokens
            # normal completions
            else:
                prompt = payload["prompt"]
                if isinstance(prompt, str):  # single prompt
                    prompt_tokens = len(encoding.encode(prompt))
                    num_tokens = prompt_tokens + completion_tokens
                    return num_tokens
                elif isinstance(prompt, list):  # multiple prompts
                    prompt_tokens = sum([len(encoding.encode(p)) for p in prompt])
                    num_tokens = prompt_tokens + completion_tokens * len(prompt)
                    return num_tokens
                else:
                    raise TypeError(
                        'Expecting either string or list of strings for "prompt" field in completion request'
                    )
        elif api_endpoint == "embeddings":
            input = payload["input"]
            if isinstance(input, str):  # single input
                num_tokens = len(encoding.encode(input))
                return num_tokens
            elif isinstance(input, list):  # multiple inputs
                num_tokens = sum([len(encoding.encode(i)) for i in input])
                return num_tokens
            else:
                raise TypeError(
                    'Expecting either string or list of strings for "inputs" field in embedding request'
                )
        else:
            raise NotImplementedError(
                f'API endpoint "{api_endpoint}" not implemented in this script'
            )
            

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
        ratelimiter = OpenAIRateLimiter,
        status_tracker = None,
        queue = None,
        endpoint=None,
    ):
        
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_key = api_key
        self.token_encoding_name=token_encoding_name,
        self.max_attempts = max_attempts,
        self.status_tracker = status_tracker or StatusTracker()
        self.queue = queue or AsyncQueue()
        self.ratelimiter=ratelimiter(max_requests_per_minute, max_tokens_per_minute),
        self.endpoint=endpoint
        
        
    async def _call_api(self, http_session, endpoint, method="post", payload: Dict[str, any] =None) -> Optional[Dict[str, any]]:
        endpoint = self.api_endpoint_from_url(self.base_url+endpoint)
        
        while True:
            if self.rate_limiter.available_request_capacity < 1 or self.rate_limiter.available_token_capacity < 10:  # Minimum token count
                await asyncio.sleep(1)  # Wait for capacity
                continue
            
            required_tokens = self.rate_limiter.calculate_num_token(payload, endpoint, self.token_encoding_name)
            
            if self.rate_limiter.available_token_capacity >= required_tokens:
                self.rate_limiter.available_request_capacity -= 1
                self.rate_limiter.available_token_capacity -= required_tokens

                request_headers = {"Authorization": f"Bearer {self.api_key}"}
                attempts_left = self.max_attempts

                while attempts_left > 0:
                    try:
                        method = self.api_methods(http_session, method)                         
                        async with method(
                            url=(self.base_url+endpoint), headers=request_headers, json=payload
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
    
    async def serve(self, schema=None, method="post", session=None, **kwargs):
        payload = self.endpoint.create_payload(self, schema=schema, **kwargs)
        
        async def call_api():
            endpoint = self.endpoint.endpoint
            async with aiohttp.ClientSession() as http_session:
                completion = await self._call_api(http_session=http_session, endpoint=endpoint, payload=payload, method=method)
                return completion           

        try:
            completion = await call_api()
        except Exception as e:
                self.status_tracker.num_tasks_failed += 1
                raise e
        
        if "choices" in completion:
            session._logger({"input":payload, "output": completion})
            session.conversation.add_messages(response=completion['choices'][0])
            session.conversation.responses.append(self.conversation.messages[-1])
            session.conversation.response_counts += 1
            session.status_tracker.num_tasks_succeeded += 1
        else:
            session.status_tracker.num_tasks_failed += 1
            
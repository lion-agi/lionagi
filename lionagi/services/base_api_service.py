import re
import asyncio
import os
import tiktoken
import logging
import aiohttp
from typing import Generator, NoReturn, Dict, Any, Optional
from .service_objs import BaseService, RateLimiter, StatusTracker, AsyncQueue

class BaseAPIRateLimiter(RateLimiter):

    def __init__(
        self, max_requests_per_minute: int, max_tokens_per_minute: int
    ) -> None:
        super().__init__(max_requests_per_minute, max_tokens_per_minute)

    @classmethod
    async def create(
        cls, max_requests_per_minute: int, max_tokens_per_minute: int
    ) -> None:
        self = cls(max_requests_per_minute, max_tokens_per_minute)
        if not os.getenv("env_readthedocs"):
            self.rate_limit_replenisher_task = await asyncio.create_task(
                self.rate_limit_replenisher()
            )
        return self

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

    def calculate_num_token(
        self,
        payload: Dict[str, Any] = None,
        api_endpoint: str = None,
        token_encoding_name: str = None,
    ) -> int:
        """
        Calculates the number of tokens required for a request based on the payload and API endpoint.

        The token calculation logic might vary based on different API endpoints and payload content.
        This method should be implemented in a subclass to provide the specific calculation logic
        for the OpenAI API.

        Parameters:
            payload (Dict[str, Any]): The payload of the request.

            api_endpoint (str): The specific API endpoint for the request.

            token_encoding_name (str): The name of the token encoding method.

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
                            num_tokens -= (
                                1  # role is always required and always 1 token
                            )
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


class BaseAPIService(BaseService):
    
    def __init__(self, api_key: str = None, 
                 status_tracker = None,
                 queue = None, endpoint=None, schema=None, 
                 ratelimiter=None, max_requests_per_minute=None, max_tokens_per_minute=None) -> None:
        self.api_key = api_key
        self.status_tracker = status_tracker or StatusTracker()
        self.queue = queue or AsyncQueue()
        self.endpoint=endpoint
        self.schema = schema
        self.rate_limiter = ratelimiter(max_requests_per_minute, max_tokens_per_minute)
    
    @staticmethod                    
    def api_methods(http_session, method="post"):
        if method not in ["post", "delete", "head", "options", "patch"]:
            raise ValueError("Invalid request, method must be in ['post', 'delete', 'head', 'options', 'patch']")
        elif method == "post":
            return http_session.post
        elif method == "delete":
            return http_session.delete
        elif method == "head":
            return http_session.head
        elif method == "options":
            return http_session.options
        elif method == "patch":
            return http_session.patch

    @staticmethod
    def api_endpoint_from_url(request_url: str) -> str:
        match = re.search(r"^https://[^/]+/v\d+/(.+)$", request_url)
        if match:
            return match.group(1)
        else:
            return ""

    @staticmethod
    def task_id_generator_function() -> Generator[int, None, None]:
        task_id = 0
        while True:
            yield task_id
            task_id += 1

    async def _call_api(self, http_session, endpoint_, method="post", payload: Dict[str, any] =None) -> Optional[Dict[str, any]]:
        endpoint_ = self.api_endpoint_from_url("https://api.openai.com/v1/"+endpoint_)
        
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
    
    async def _serve(self, payload, endpoint_="chat/completions", method="post"):
         
        async def call_api():
            async with aiohttp.ClientSession() as http_session:
                completion = await self._call_api(http_session=http_session, endpoint_=endpoint_, payload=payload, method=method)
                return completion

        try:
            return await call_api()
        except Exception as e:
                self.status_tracker.num_tasks_failed += 1
                raise e
            
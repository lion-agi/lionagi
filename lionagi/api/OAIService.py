import asyncio
import logging
import tiktoken
from typing import Optional

from .StatusTracker import StatusTracker
from .AsyncQueue import AsyncQueue
from .BaseAPIService import BaseAPIService
from .RateLimiter import RateLimiter


class OpenAIRateLimiter(RateLimiter):
    """
    A specialized RateLimiter for OpenAI API.

    Extends the generic RateLimiter to apply replenishing logic specific to
    OpenAI's rate limits.
    """
    
    def __init__(self, max_requests_per_minute: int, max_tokens_per_minute: int):
        """
        Initialize the rate limiter with specific limits for OpenAI API.

        Args:
            max_requests_per_minute: The maximum number of requests allowed per minute.
            max_tokens_per_minute: The maximum number of tokens allowed per minute.
        """
        super().__init__(max_requests_per_minute, max_tokens_per_minute)
    
    async def rate_limit_replenisher(self, interval: int = 60) -> None:
        """
        Replenish the rate limits at a regular interval.

        Args:
            interval: The interval (in seconds) at which to replenish the rate limits.
        """
        while not self._stop_event.is_set():
            await asyncio.sleep(interval)
            self.available_request_capacity = self.max_requests_per_minute
            self.available_token_capacity = self.max_tokens_per_minute
            
    def num_tokens_consumed_from_request(self, payload: dict, api_endpoint: str) -> int:
        """
        Calculate the number of tokens that a request will consume.

        Args:
            payload: The payload of the request to be sent to the API.
            api_endpoint: The endpoint of the API to which the request will be sent.

        Returns:
            The number of tokens the request will consume.

        Raises:
            TypeError: If the payload format is not as expected.
            NotImplementedError: If the API endpoint isn't accounted for in the calculations.
        """
        encoding = tiktoken.get_encoding(self.token_encoding_name)
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

    Provides methods for calling the API endpoints and handling response data.
    """

    base_url = "https://api.openai.com/v1/"

    def __init__(
        self,
        api_key: str,
        token_encoding_name: str,
        max_attempts: int,
        status_tracker: Optional[StatusTracker] = None,
        rate_limiter: Optional[OpenAIRateLimiter] = None,
        queue: Optional[AsyncQueue] = None
    ):
        """
        Initialize the OpenAI service with an API key and configuration.

        Args:
            api_key: The API key for authenticating with OpenAI.
            token_encoding_name: The name of the text encoding used by OpenAI.
            max_attempts: The maximum number of attempts for calling an API endpoint.
            status_tracker: An optional tracker for API call outcomes.
            rate_limiter: An optional rate limiter specific to OpenAI's limits.
            queue: An optional queue for managing asynchronous API calls.
        """
        super().__init__(api_key=api_key, 
                         token_encoding_name=token_encoding_name, 
                         max_attempts=max_attempts, 
                         status_tracker=status_tracker, 
                         rate_limiter=rate_limiter,  
                         queue=queue)

    async def call_api(self, session, request_url: str, payload: dict) -> Optional[dict]:
        """
        Call the OpenAI API with a given payload and handle the response.

        Args:
            session: The session object used to make HTTP requests.
            request_url: The full URL of the API endpoint to call.
            payload: The payload to send in the API request.

        Returns:
            A dictionary with the response data from the API call or None if failed.

        Raises:
            asyncio.TimeoutError: If the request attempts exceed the maximum limit.
        """
        while True:
            if self.available_request_capacity < 1 or self.available_token_capacity < 10:  # Minimum token count
                await asyncio.sleep(1)  # Wait for capacity
                continue
            
            endpoint = self.api_endpoint_from_url(request_url)
            required_tokens = self.rate_limiter.num_tokens_consumed_from_request(payload, endpoint)
            
            if self.available_token_capacity >= required_tokens:
                self.available_request_capacity -= 1
                self.available_token_capacity -= required_tokens

                request_headers = {"Authorization": f"Bearer {self.api_key}"}
                attempts_left = self.max_attempts

                while attempts_left > 0:
                    try:
                        async with session.post(
                            url=request_url, headers=request_headers, json=payload
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
                await asyncio.sleep(1)  # Wait for token capacity
                
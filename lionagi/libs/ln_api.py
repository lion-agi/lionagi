import asyncio
import contextlib
import logging
import re
from abc import ABC
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, NoReturn, Type

import aiohttp

import lionagi.libs.ln_func_call as func_call
from lionagi.libs.ln_async import AsyncUtil
from lionagi.libs.ln_convert import strip_lower, to_dict, to_str
from lionagi.libs.ln_nested import nget


class APIUtil:
    """
    A utility class for assisting with common API usage patterns.
    """

    @staticmethod
    def api_method(
        http_session: aiohttp.ClientSession, method: str = "post"
    ) -> Callable:
        """
        Returns the corresponding HTTP method function from the http_session object.

        Args:
                http_session: The session object from the aiohttp library.
                method: The HTTP method as a string.

        Returns:
                The Callable for the specified HTTP method.

        Raises:
                ValueError: If the method is not one of the allowed ones.

        Examples:
                >>> session = aiohttp.ClientSession()
                >>> post_method = APIUtil.api_method(session, "post")
                >>> print(post_method)
                <bound method ClientSession._request of <aiohttp.client.ClientSession object at 0x...>>
        """
        if method in {"post", "delete", "head", "options", "patch"}:
            return getattr(http_session, method)
        else:
            raise ValueError(
                "Invalid request, method must be in ['post', 'delete', 'head', 'options', 'patch']"
            )

    @staticmethod
    def api_error(response_json: Mapping[str, Any]) -> bool:
        """
        Checks if the given response_json dictionary contains an "error" key.

        Args:
                response_json: The JSON assistant_response as a dictionary.

        Returns:
                True if there is an error, False otherwise.

        Examples:
                >>> response_json_with_error = {"error": "Something went wrong"}
                >>> APIUtil.api_error(response_json_with_error)
                True
                >>> response_json_without_error = {"result": "Success"}
                >>> APIUtil.api_error(response_json_without_error)
                False
        """
        if "error" in response_json:
            logging.warning(
                f"API call failed with error: {response_json['error']}"
            )
            return True
        return False

    @staticmethod
    def api_rate_limit_error(response_json: Mapping[str, Any]) -> bool:
        """
        Checks if the error message in the response_json dictionary contains the phrase "Rate limit".

        Args:
                response_json: The JSON assistant_response as a dictionary.

        Returns:
                True if the phrase "Rate limit" is found, False otherwise.

        Examples:
                >>> response_json_with_rate_limit = {"error": {"message": "Rate limit exceeded"}}
                >>> api_rate_limit_error(response_json_with_rate_limit)
                True
                >>> response_json_without_rate_limit = {"error": {"message": "Another error"}}
                >>> api_rate_limit_error(response_json_without_rate_limit)
                False
        """
        return "Rate limit" in response_json.get("error", {}).get(
            "message", ""
        )

    @staticmethod
    @func_call.lru_cache(maxsize=128)
    def api_endpoint_from_url(request_url: str) -> str:
        """
        Extracts the API endpoint from a given URL using a regular expression.

        Args:
                request_url: The full URL to the API endpoint.

        Returns:
                The extracted endpoint or an empty string if the pattern does not match.

        Examples:
                >>> valid_url = "https://api.example.com/v1/users"
                >>> api_endpoint_from_url(valid_url)
                'users'
                >>> invalid_url = "https://api.example.com/users"
                >>> api_endpoint_from_url(invalid_url)
                ''
        """
        match = re.search(r"^https://[^/]+(/.+)?/v\d+/(.+)$", request_url)
        return match[2] if match else ""

    @staticmethod
    async def unified_api_call(
        http_session: aiohttp.ClientSession, method: str, url: str, **kwargs
    ) -> Any:
        """
        Makes an API call and automatically retries on rate limit error.

        Args:
                http_session: The session object from the aiohttp library.
                method: The HTTP method as a string.
                url: The URL to which the request is made.
                **kwargs: Additional keyword arguments to pass to the API call.

        Returns:
                The JSON assistant_response as a dictionary.

        Examples:
                >>> session = aiohttp.ClientSession()
                >>> success_url = "https://api.example.com/v1/success"
                >>> print(await unified_api_call(session, 'get', success_url))
                {'result': 'Success'}
                >>> rate_limit_url = "https://api.example.com/v1/rate_limit"
                >>> print(await unified_api_call(session, 'get', rate_limit_url))
                {'error': {'message': 'Rate limit exceeded'}}
        """
        api_call = APIUtil.api_method(http_session, method)
        retry_count = 3
        retry_delay = 5  # seconds

        for attempt in range(retry_count):
            async with api_call(url, **kwargs) as response:
                response_json = await response.json()

                if not APIUtil.api_error(response_json):
                    return response_json

                if (
                    APIUtil.api_rate_limit_error(response_json)
                    and attempt < retry_count - 1
                ):
                    logging.warning(
                        f"Rate limit error detected. Retrying in {retry_delay} seconds..."
                    )
                    await AsyncUtil.sleep(retry_delay)
                else:
                    break

        return response_json

    @staticmethod
    def get_cache_key(url: str, params: Mapping[str, Any] | None) -> str:
        """
        Creates a unique cache key based on the URL and parameters.
        """
        import hashlib

        param_str = to_str(params, sort_keys=True) if params else ""
        return hashlib.md5((url + param_str).encode("utf-8")).hexdigest()

    @staticmethod
    async def retry_api_call(
        http_session: aiohttp.ClientSession,
        url: str,
        retries: int = 3,
        backoff_factor: float = 0.5,
        **kwargs,
    ) -> Any:
        """
        Retries an API call on failure, with exponential backoff.

        Args:
                http_session: The aiohttp client session.
                url: The URL to make the API call.
                retries: The number of times to retry.
                backoff_factor: The backoff factor for retries.
                **kwargs: Additional arguments for the API call.

        Returns:
                The assistant_response from the API call, if successful; otherwise, None.
        """
        for attempt in range(retries):
            try:
                async with http_session.get(url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError:
                if attempt < retries - 1:
                    delay = backoff_factor * (2**attempt)
                    logging.info(f"Retrying {url} in {delay} seconds...")
                    await AsyncUtil.sleep(delay)
                else:
                    logging.error(
                        f"Failed to retrieve data from {url} after {retries} attempts."
                    )
                    return None

    @staticmethod
    async def upload_file_with_retry(
        http_session: aiohttp.ClientSession,
        url: str,
        file_path: str,
        param_name: str = "file",
        additional_data: Mapping[str, Any] = None,
        retries: int = 3,
    ) -> Any:
        """
        Uploads a file to a specified URL with a retry mechanism for handling failures.

        Args:
                http_session: The HTTP session object to use for making the request.
                url: The URL to which the file will be uploaded.
                file_path: The path to the file that will be uploaded.
                param_name: The name of the parameter expected by the server for the file upload.
                additional_data: Additional data to be sent with the upload.
                retries: The number of times to retry the upload in case of failure.

        Returns:
                The HTTP assistant_response object.

        Examples:
                >>> session = aiohttp.ClientSession()
                >>> assistant_response = await APIUtil.upload_file_with_retry(session, 'http://example.com/upload', 'path/to/file.txt')
                >>> assistant_response.status
                200
        """
        for attempt in range(retries):
            try:
                with open(file_path, "rb") as file:
                    files = {param_name: file}
                    additional_data = additional_data or {}
                    async with http_session.post(
                        url, data={**files, **additional_data}
                    ) as response:
                        response.raise_for_status()
                        return await response.json()
            except aiohttp.ClientError as e:
                if attempt == retries - 1:
                    raise e
                backoff = 2**attempt
                logging.info(f"Retrying {url} in {backoff} seconds...")
                await AsyncUtil.sleep(backoff)

    @staticmethod
    @AsyncUtil.cached(ttl=10 * 60)  # Cache the result for 10 minutes
    async def get_oauth_token_with_cache(
        http_session: aiohttp.ClientSession,
        auth_url: str,
        client_id: str,
        client_secret: str,
        scope: str,
    ) -> str:
        """
        Retrieves an OAuth token from the authentication server and caches it to avoid unnecessary requests.

        Args:
                http_session: The HTTP session object to use for making the request.
                auth_url: The URL of the authentication server.
                client_id: The client ID for OAuth authentication.
                client_secret: The client secret for OAuth authentication.
                scope: The scope for which the OAuth token is requested.

        Returns:
                The OAuth token as a string.

        Examples:
                >>> session = aiohttp.ClientSession()
                >>> token = await APIUtil.get_oauth_token_with_cache(session, 'http://auth.example.com', 'client_id', 'client_secret', 'read')
                >>> token
                'mock_access_token'
        """
        async with http_session.post(
            auth_url,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": scope,
            },
        ) as auth_response:
            auth_response.raise_for_status()
            return (await auth_response.json()).get("access_token")

    @staticmethod
    @AsyncUtil.cached(ttl=10 * 60)
    async def cached_api_call(
        http_session: aiohttp.ClientSession, url: str, **kwargs
    ) -> Any:
        """
        Makes an API call.

        Args:
                http_session: The aiohttp client session.
                url: The URL for the API call.
                **kwargs: Additional arguments for the API call.

        Returns:
                The assistant_response from the API call, if successful; otherwise, None.
        """
        try:
            async with http_session.get(url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logging.error(f"API call to {url} failed: {e}")
            return None

    @staticmethod
    def calculate_num_token(
        payload: Mapping[str, Any] = None,
        api_endpoint: str = None,
        token_encoding_name: str = None,
    ) -> int:  # sourcery skip: avoid-builtin-shadow
        """
        Calculates the number of tokens required for a request based on the payload and API endpoint.

        The token calculation logic might vary based on different API endpoints and payload content.
        This method should be implemented in a subclass to provide the specific calculation logic
        for the OpenAI API.

        Parameters:
                payload (Mapping[str, Any]): The payload of the request.

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
        import tiktoken

        from .ln_image import ImageUtil

        token_encoding_name = token_encoding_name or "cl100k_base"
        encoding = tiktoken.get_encoding(token_encoding_name)
        if api_endpoint.endswith("completions"):
            max_tokens = payload.get("max_tokens", 15)
            n = payload.get("n", 1)
            completion_tokens = n * max_tokens
            if api_endpoint.startswith("chat/"):
                num_tokens = 0

                for message in payload["messages"]:
                    num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n

                    _content = message.get("content")
                    if isinstance(_content, str):
                        num_tokens += len(encoding.encode(_content))

                    elif isinstance(_content, list):
                        for item in _content:
                            if isinstance(item, dict):
                                if "text" in item:
                                    num_tokens += len(
                                        encoding.encode(to_str(item["text"]))
                                    )
                                elif "image_url" in item:
                                    a: str = item["image_url"]["url"]
                                    if "data:image/jpeg;base64," in a:
                                        a = a.split("data:image/jpeg;base64,")[
                                            1
                                        ].strip()
                                    num_tokens += ImageUtil.calculate_image_token_usage_from_base64(
                                        a, item.get("detail", "low")
                                    )
                                    num_tokens += 20  # for every image we add 20 tokens buffer
                            elif isinstance(item, str):
                                num_tokens += len(encoding.encode(item))
                            else:
                                num_tokens += len(encoding.encode(str(item)))

                num_tokens += (
                    2  # every reply is primed with <im_start>assistant
                )
                return num_tokens + completion_tokens
            else:
                prompt = payload["format_prompt"]
                if isinstance(prompt, str):  # single format_prompt
                    prompt_tokens = len(encoding.encode(prompt))
                    return prompt_tokens + completion_tokens
                elif isinstance(prompt, list):  # multiple prompts
                    prompt_tokens = sum(
                        len(encoding.encode(p)) for p in prompt
                    )
                    return prompt_tokens + completion_tokens * len(prompt)
                else:
                    raise TypeError(
                        'Expecting either string or list of strings for "format_prompt" field in completion request'
                    )
        elif api_endpoint == "embeddings":
            input = payload["input"]
            if isinstance(input, str):  # single input
                return len(encoding.encode(input))
            elif isinstance(input, list):  # multiple inputs
                return sum(len(encoding.encode(i)) for i in input)
            else:
                raise TypeError(
                    'Expecting either string or list of strings for "inputs" field in embedding request'
                )
        else:
            raise NotImplementedError(
                f'API endpoint "{api_endpoint}" not implemented in this script'
            )

    @staticmethod
    def create_payload(
        input_, config, required_, optional_, input_key, **kwargs
    ):
        config = {**config, **kwargs}
        payload = {input_key: input_}

        for key in required_:
            payload[key] = config[key]

        for key in optional_:
            if bool(config[key]) and strip_lower(config[key]) != "none":
                payload[key] = config[key]

        return payload


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
            interval: The time interval in seconds for replenishing capacities.
            max_requests: The maximum number of requests allowed per interval.
            max_tokens: The maximum number of tokens allowed per interval.
            available_request_capacity: The current available request capacity.
            available_token_capacity: The current available token capacity.
            rate_limit_replenisher_task: The asyncio task for replenishing capacities.
    """

    def __init__(
        self,
        max_requests: int,
        max_tokens: int,
        interval: int = 60,
        token_encoding_name=None,
    ) -> None:
        self.interval: int = interval
        self.max_requests: int = max_requests
        self.max_tokens: int = max_tokens
        self.available_request_capacity: int = max_requests
        self.available_token_capacity: int = max_tokens
        self.rate_limit_replenisher_task: AsyncUtil.Task | None = None
        self._stop_replenishing: AsyncUtil.Event = AsyncUtil.create_event()
        self._lock: AsyncUtil.Lock = AsyncUtil.create_lock()
        self.token_encoding_name = token_encoding_name

    async def start_replenishing(self) -> NoReturn:
        """Starts the replenishment of rate limit capacities at regular intervals."""
        try:
            while not self._stop_replenishing.is_set():
                await AsyncUtil.sleep(self.interval)
                async with self._lock:
                    self.available_request_capacity = self.max_requests
                    self.available_token_capacity = self.max_tokens
        except asyncio.CancelledError:
            logging.info("Rate limit replenisher task cancelled.")
        except Exception as e:
            logging.error(
                f"An error occurred in the rate limit replenisher: {e}"
            )

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
            if (
                self.available_request_capacity > 0
                and self.available_token_capacity > 0
            ):
                self.available_request_capacity -= 1
                self.available_token_capacity -= (
                    required_tokens
                    # Assuming 1 token per request for simplicity
                )
                return True
            return False

    async def _call_api(
        self,
        http_session,
        endpoint: str,
        base_url: str,
        api_key: str,
        max_attempts: int = 3,
        method: str = "post",
        payload: Mapping[str, any] = None,
        required_tokens: int = None,
        **kwargs,
    ) -> Mapping[str, any] | None:
        """
        Makes an API call to the specified endpoint using the provided HTTP session.

        Args:
                http_session: The aiohttp client session to use for the API call.
                endpoint: The API endpoint to call.
                base_url: The base URL of the API.
                api_key: The API key for authentication.
                max_attempts: The maximum number of attempts for the API call.
                method: The HTTP method to use for the API call.
                payload: The payload to send with the API call.

        Returns:
                The JSON assistant_response from the API call if successful, otherwise None.
        """
        endpoint = APIUtil.api_endpoint_from_url(base_url + endpoint)
        while True:
            if (
                self.available_request_capacity < 1
                or self.available_token_capacity < 10
            ):  # Minimum token count
                await AsyncUtil.sleep(1)  # Wait for capacity
                continue

            if not required_tokens:
                required_tokens = APIUtil.calculate_num_token(
                    payload, endpoint, self.token_encoding_name, **kwargs
                )

            if await self.request_permission(required_tokens):
                request_headers = {"Authorization": f"Bearer {api_key}"}
                attempts_left = max_attempts

                while attempts_left > 0:
                    try:
                        method = APIUtil.api_method(http_session, method)
                        async with method(
                            url=(base_url + endpoint),
                            headers=request_headers,
                            json=payload,
                        ) as response:
                            response_json = await response.json()

                            if "error" not in response_json:
                                return response_json
                            logging.warning(
                                f"API call failed with error: {response_json['error']}"
                            )
                            attempts_left -= 1

                            if "Rate limit" in response_json["error"].get(
                                "message", ""
                            ):
                                await AsyncUtil.sleep(15)
                    except Exception as e:
                        logging.warning(f"API call failed with exception: {e}")
                        attempts_left -= 1

                logging.error("API call failed after all attempts.")
                break
            else:
                await AsyncUtil.sleep(1)

    @classmethod
    async def create(
        cls,
        max_requests: int,
        max_tokens: int,
        interval: int = 60,
        token_encoding_name=None,
    ) -> "BaseRateLimiter":
        """
        Creates an instance of BaseRateLimiter and starts the replenisher task.

        Args:
                max_requests: The maximum number of requests allowed per interval.
                max_tokens: The maximum number of tokens allowed per interval.
                interval: The time interval in seconds for replenishing capacities.
                token_encoding_name: The name of the token encoding to use.

        Returns:
                An instance of BaseRateLimiter with the replenisher task started.
        """
        instance = cls(max_requests, max_tokens, interval, token_encoding_name)
        instance.rate_limit_replenisher_task = AsyncUtil.create_task(
            instance.start_replenishing(), obj=False
        )
        return instance


class SimpleRateLimiter(BaseRateLimiter):
    """
    A simple implementation of a rate limiter.

    Inherits from BaseRateLimiter and provides a basic rate limiting mechanism.
    """

    def __init__(
        self,
        max_requests: int,
        max_tokens: int,
        interval: int = 60,
        token_encoding_name=None,
    ) -> None:
        """Initializes the SimpleRateLimiter with the specified parameters."""
        super().__init__(
            max_requests, max_tokens, interval, token_encoding_name
        )


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
            config (Mapping): Configuration parameters for the endpoint.
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
        endpoint_: str | None = None,
        rate_limiter_class: type[BaseRateLimiter] = SimpleRateLimiter,
        token_encoding_name=None,
        config: Mapping = None,
    ) -> None:
        self.endpoint = endpoint_ or "chat/completions"
        self.rate_limiter_class = rate_limiter_class
        self.max_requests = max_requests
        self.max_tokens = max_tokens
        self.interval = interval
        self.token_encoding_name = token_encoding_name
        self.config = config or {}
        self.rate_limiter: BaseRateLimiter | None = None
        self._has_initialized = False

    async def init_rate_limiter(self) -> None:
        """Initializes the rate limiter for the endpoint."""
        self.rate_limiter = await self.rate_limiter_class.create(
            self.max_requests,
            self.max_tokens,
            self.interval,
            self.token_encoding_name,
        )
        self._has_initialized = True


class BaseService:
    """
    Base class for services that interact with API endpoints.

    This class provides a foundation for services that need to make API calls with rate limiting.

    Attributes:
            api_key (Optional[str]): The API key used for authentication.
            schema (Mapping[str, Any]): The schema defining the service's endpoints.
            status_tracker (StatusTracker): The object tracking the status of API calls.
            endpoints (Mapping[str, EndPoint]): A dictionary of endpoint objects.
    """

    base_url: str = ""
    available_endpoints: list = []

    def __init__(
        self,
        api_key: str | None = None,
        schema: Mapping[str, Any] = None,
        token_encoding_name: str = None,
        max_tokens: int = 100_000,
        max_requests: int = 1_000,
        interval: int = 60,
    ) -> None:
        self.api_key = api_key
        self.schema = schema or {}
        self.status_tracker = StatusTracker()
        self.endpoints: Mapping[str, EndPoint] = {}
        self.token_encoding_name = token_encoding_name
        self.chat_config_rate_limit = {
            "max_requests": max_requests,
            "max_tokens": max_tokens,
            "interval": interval,
        }

    async def init_endpoint(
        self,
        endpoint_: Sequence | str | EndPoint | None = None,
    ) -> None:
        """
        Initializes the specified endpoint or all endpoints if none is specified.

        Args:
                endpoint_: The endpoint(s) to initialize. Can be a string, an EndPoint, a list of strings, or a list of EndPoints.
        """

        if endpoint_:
            if not isinstance(endpoint_, list):
                endpoint_ = [endpoint_]
            for ep in endpoint_:
                if ep not in self.available_endpoints:
                    raise ValueError(
                        f"Endpoint {ep} not available for service {self.__class__.__name__}"
                    )

                if ep not in self.endpoints:
                    endpoint_config = nget(self.schema, [ep, "config"])
                    self.schema.get(ep, {})
                    if isinstance(ep, EndPoint):
                        self.endpoints[ep.endpoint] = ep
                    elif ep == "chat/completions":
                        self.endpoints[ep] = EndPoint(
                            max_requests=self.chat_config_rate_limit.get(
                                "max_requests", 1000
                            ),
                            max_tokens=self.chat_config_rate_limit.get(
                                "max_tokens", 100000
                            ),
                            interval=self.chat_config_rate_limit.get(
                                "interval", 60
                            ),
                            endpoint_=ep,
                            token_encoding_name=self.token_encoding_name,
                            config=endpoint_config,
                        )
                    else:
                        self.endpoints[ep] = EndPoint(
                            max_requests=(
                                endpoint_config.get("max_requests", 1000)
                                if endpoint_config.get("max_requests", 1000)
                                is not None
                                else 1000
                            ),
                            max_tokens=(
                                endpoint_config.get("max_tokens", 100000)
                                if endpoint_config.get("max_tokens", 100000)
                                is not None
                                else 100000
                            ),
                            interval=(
                                endpoint_config.get("interval", 60)
                                if endpoint_config.get("interval", 60)
                                is not None
                                else 60
                            ),
                            endpoint_=ep,
                            token_encoding_name=self.token_encoding_name,
                            config=endpoint_config,
                        )

                if not self.endpoints[ep]._has_initialized:
                    await self.endpoints[ep].init_rate_limiter()

        else:
            for ep in self.available_endpoints:
                endpoint_config = nget(self.schema, [ep, "config"])
                self.schema.get(ep, {})
                if ep not in self.endpoints:
                    self.endpoints[ep] = EndPoint(
                        max_requests=endpoint_config.get("max_requests", 1000),
                        max_tokens=endpoint_config.get("max_tokens", 100000),
                        interval=endpoint_config.get("interval", 60),
                        endpoint_=ep,
                        token_encoding_name=self.token_encoding_name,
                        config=endpoint_config,
                    )
                if not self.endpoints[ep]._has_initialized:
                    await self.endpoints[ep].init_rate_limiter()

    async def call_api(
        self, payload, endpoint, method, required_tokens=None, **kwargs
    ):
        """
        Calls the specified API endpoint with the given payload and method.

        Args:
                payload: The payload to send with the API call.
                endpoint: The endpoint to call.
                method: The HTTP method to use for the call.

        Returns:
                The assistant_response from the API call.

        Raises:
                ValueError: If the endpoint has not been initialized.
        """
        if endpoint not in self.endpoints.keys():
            raise ValueError(f"The endpoint {endpoint} has not initialized.")
        async with aiohttp.ClientSession() as http_session:
            return await self.endpoints[endpoint].rate_limiter._call_api(
                http_session=http_session,
                endpoint=endpoint,
                base_url=self.base_url,
                api_key=self.api_key,
                method=method,
                payload=payload,
                required_tokens=required_tokens,
                **kwargs,
            )


class PayloadPackage:

    @classmethod
    def embeddings(cls, embed_str, llmconfig, schema, **kwargs):
        return APIUtil.create_payload(
            input_=embed_str,
            config=llmconfig,
            required_=schema["required"],
            optional_=schema["optional"],
            input_key="input",
            **kwargs,
        )

    @classmethod
    def chat_completion(cls, messages, llmconfig, schema, **kwargs):
        """
        Creates a payload for the chat completion operation.

        Args:
                messages: The messages to include in the chat completion.
                llmconfig: Configuration for the language model.
                schema: The schema describing required and optional fields.
                **kwargs: Additional keyword arguments.

        Returns:
                The constructed payload.
        """
        return APIUtil.create_payload(
            input_=messages,
            config=llmconfig,
            required_=schema["required"],
            optional_=schema["optional"],
            input_key="messages",
            **kwargs,
        )

    @classmethod
    def fine_tuning(cls, training_file, llmconfig, schema, **kwargs):
        """
        Creates a payload for the fine-tuning operation.

        Args:
                training_file: The file containing training data.
                llmconfig: Configuration for the language model.
                schema: The schema describing required and optional fields.
                **kwargs: Additional keyword arguments.

        Returns:
                The constructed payload.
        """
        return APIUtil.create_payload(
            input_=training_file,
            config=llmconfig,
            required_=schema["required"],
            optional_=schema["optional"],
            input_key="training_file",
            **kwargs,
        )

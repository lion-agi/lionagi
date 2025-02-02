# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import json
import logging
from abc import ABC
from collections.abc import AsyncGenerator
from typing import Any, Literal

import aiohttp
from aiocache import cached
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Self

from lionagi._errors import ExecutionError, RateLimitError
from lionagi.protocols.generic.event import Event, EventStatus
from lionagi.settings import Settings

from .token_calculator import TokenCalculator


class EndpointConfig(BaseModel):
    """Represents configuration data for an API endpoint.

    Attributes:
        provider (str | None):
            The name of the API provider (e.g., "openai").
        base_url (str | None):
            The base URL for the endpoint, if any.
        endpoint (str):
            The endpoint path or identifier (e.g., "/v1/chat/completions").
        endpoint_params (dict | None):
            Key-value pairs for dynamic endpoint formatting.
        method (Literal["get","post","put","delete"]):
            The HTTP method used when calling this endpoint.
        openai_compatible (bool):
            If True, indicates that the endpoint expects OpenAI-style requests.
        required_kwargs (set[str]):
            The names of required parameters for this endpoint.
        optional_kwargs (set[str]):
            The names of optional parameters for this endpoint.
        deprecated_kwargs (set[str]):
            The names of parameters that may still be accepted but are
            deprecated.
        is_invokeable (bool):
            Whether this endpoint supports direct invocation.
        is_streamable (bool):
            Whether this endpoint supports streaming responses.
        requires_tokens (bool):
            Whether tokens must be calculated before sending a request.
        api_version (str | None):
            An optional version string for the API.
        allowed_roles (list[str] | None):
            If set, only these roles are allowed in message or conversation
            data.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
        populate_by_name=True,
        use_enum_values=True,
    )

    name: str | None = None
    provider: str | None = None
    base_url: str | None = None
    endpoint: str
    endpoint_params: dict | None = None
    method: Literal["get", "post", "put", "delete"] = Field("post")
    openai_compatible: bool = False
    required_kwargs: set[str] = Field(default_factory=set)
    optional_kwargs: set[str] = Field(default_factory=set)
    deprecated_kwargs: set[str] = Field(default_factory=set)
    is_invokeable: bool = False
    is_streamable: bool = False
    requires_tokens: bool = False
    api_version: str | None = None
    allowed_roles: list[str] | None = None
    request_options: type | None = Field(None, exclude=True)
    invoke_with_endpoint: bool | None = None


class EndPoint(ABC):
    """Abstract base class representing an API endpoint.

    This class wraps an `EndpointConfig` and provides methods for creating and
    invoking API payloads, optionally with caching or streaming. Concrete
    implementations should override `_invoke` and `_stream` to perform actual
    HTTP requests.
    """

    def __init__(
        self, config: dict | EndpointConfig | type[EndpointConfig], **kwargs
    ) -> None:
        """Initializes the EndPoint with a given configuration.

        Args:
            config (dict | EndpointConfig): Configuration data that matches the EndpointConfig
                schema.
        """
        if isinstance(config, dict):
            self.config = EndpointConfig(**config)
        if isinstance(config, EndpointConfig):
            self.config = config
        if isinstance(config, type) and issubclass(config, EndpointConfig):
            self.config = config()
        if kwargs:
            self.update_config(**kwargs)

    def update_config(self, **kwargs):
        config = self.config.model_dump()
        config.update(kwargs)
        self.config = self.config.model_validate(config)

    @property
    def name(self) -> str | None:
        """str | None: The name of the endpoint, if any."""
        return self.config.name or self.endpoint

    @property
    def is_streamable(self) -> bool:
        """bool: Whether this endpoint supports streaming responses."""
        return self.config.is_streamable

    @property
    def requires_tokens(self) -> bool:
        """bool: Indicates if token calculation is needed before requests."""
        return self.config.requires_tokens

    @property
    def openai_compatible(self) -> bool:
        """bool: Whether requests conform to OpenAI's API style."""
        return self.config.openai_compatible

    @property
    def is_invokeable(self) -> bool:
        """bool: Whether this endpoint supports direct invocation."""
        return self.config.is_invokeable

    @property
    def required_kwargs(self) -> set[str]:
        """set[str]: A set of parameter names required by this endpoint."""
        return self.config.required_kwargs

    @property
    def optional_kwargs(self) -> set[str]:
        """set[str]: A set of parameter names optionally accepted."""
        return self.config.optional_kwargs

    @property
    def deprecated_kwargs(self) -> set[str]:
        """set[str]: A set of deprecated parameter names."""
        return self.config.deprecated_kwargs

    @property
    def endpoint_params(self) -> dict | None:
        """dict | None: Additional parameters to format the endpoint path."""
        return self.config.endpoint_params

    @property
    def method(self) -> str:
        """str: The HTTP method used when invoking this endpoint."""
        return self.config.method

    @property
    def endpoint(self) -> str:
        """str: The endpoint path or identifier."""
        return self.config.endpoint

    @property
    def acceptable_kwargs(self) -> set[str]:
        """set[str]: All parameters that are not explicitly prohibited."""
        return (
            self.required_kwargs
            | self.optional_kwargs
            | self.deprecated_kwargs
        )

    @property
    def full_url(self) -> str:
        """str: The complete URL, including base_url and any parameters."""
        if self.config.endpoint_params:
            return self.config.base_url + self.config.endpoint.format(
                **self.endpoint_params
            )
        return self.config.base_url + "/" + self.config.endpoint

    @property
    def allowed_roles(self) -> list[str] | None:
        """list[str] | None: A list of allowed roles, if any."""
        return self.config.allowed_roles

    @property
    def sequential_exchange(self) -> bool:
        """bool: True if this endpoint requires exactly two roles (e.g., user & assistant)."""
        if self.allowed_roles:
            return len(self.allowed_roles) == 2
        return False

    @property
    def roled(self) -> bool:
        """bool: Indicates if this endpoint uses role-based messages."""
        return self.allowed_roles is not None

    @property
    def request_options(self) -> type | None:
        return self.config.request_options

    def create_payload(self, **kwargs) -> dict:
        """Generates a request payload (and headers) for this endpoint.

        Args:
            **kwargs:
                Arbitrary parameters passed by the caller.

        Returns:
            dict:
                A dictionary containing:
                - "payload": A dict with filtered parameters for the request.
                - "headers": A dict of additional headers (e.g., `Authorization`).
                - "is_cached": Whether the request is to be cached.
        """
        payload = {}
        is_cached = kwargs.get("is_cached", False)
        headers = kwargs.get("headers", {})
        for k, v in kwargs.items():
            if k in self.acceptable_kwargs:
                payload[k] = v
        if "api_key" in kwargs:
            headers["Authorization"] = f"Bearer {kwargs['api_key']}"
        return {
            "payload": payload,
            "headers": headers,
            "is_cached": is_cached,
        }

    async def invoke(
        self,
        payload: dict,
        headers: dict,
        is_cached: bool = False,
        **kwargs,
    ):
        """Invokes this endpoint with the given payload and headers.

        Args:
            payload (dict):
                The request data to send.
            headers (dict):
                Extra HTTP headers for the request.
            is_cached (bool):
                Whether caching should be applied to this request.
            **kwargs:
                Additional arguments for the invocation.

        Returns:
            The result of the `_invoke` or `_cached_invoke` method.
        """
        if is_cached:
            return await self._cached_invoke(payload, headers, **kwargs)
        return await self._invoke(payload, headers, **kwargs)

    async def _invoke(self, payload: dict, headers: dict, **kwargs) -> Any:
        """Performs the actual HTTP request for non-streaming endpoints.

        Subclasses should implement this to make an HTTP request using
        `payload` and `headers`.

        Args:
            payload (dict): The JSON body or form data for the request.
            headers (dict): Any additional headers (e.g., auth tokens).
            **kwargs: Additional arguments.

        Returns:
            Any: The response data from the API.

        Raises:
            NotImplementedError: If the subclass has not overridden this method.
        """
        raise NotImplementedError

    async def _stream(self, payload: dict, headers: dict, **kwargs) -> Any:
        """Streams data from the endpoint if supported.

        Subclasses should implement this if streaming is supported.

        Args:
            payload (dict): The data to send.
            headers (dict): Additional headers.

        Raises:
            NotImplementedError:
                If the subclass has not overridden this for streaming endpoints.
        """
        raise NotImplementedError

    @cached(**Settings.API.CACHED_CONFIG)
    async def _cached_invoke(self, payload: dict, headers: dict, **kwargs):
        """Cached version of `_invoke` using aiocache.

        Args:
            payload (dict): The data to send in the request.
            headers (dict): Extra headers to include.
            **kwargs: Additional arguments for `_invoke`.

        Returns:
            Any: Cached or newly obtained response data.
        """
        return await self._invoke(payload, headers, **kwargs)

    def calculate_tokens(self, payload: dict) -> int:
        """Calculates the number of tokens needed for a request.

        Uses the `TokenCalculator` if the endpoint requires token counting.

        Args:
            payload (dict):
                The request data, possibly containing "messages" for chat
                or an "embed" request.

        Returns:
            int: The estimated number of tokens used.
        """
        if self.requires_tokens:
            if "messages" in payload:
                return TokenCalculator.calculate_message_tokens(
                    payload["messages"]
                )
            if "embed" in self.full_url:
                return TokenCalculator.calcualte_embed_token(**payload)
        return 0


class APICalling(Event):
    """Represents an API call event, storing payload, headers, and endpoint info.

    This class extends `Event` and provides methods to invoke or stream the
    request asynchronously. It also can track token usage and stores the
    result or any errors in `execution`.

    Attributes:
        payload (dict):
            The body or parameters for the API request.
        headers (dict):
            Additional headers (excluded from serialization).
        endpoint (EndPoint):
            The endpoint to which this request will be sent.
        is_cached (bool):
            Whether to use cached responses.
        should_invoke_endpoint (bool):
            If False, the request may not actually call the API.
    """

    payload: dict
    headers: dict = Field(exclude=True)
    endpoint: EndPoint = Field(exclude=True)
    is_cached: bool = Field(default=False, exclude=True)
    should_invoke_endpoint: bool = Field(default=True, exclude=True)
    include_token_usage_to_model: bool = Field(
        default=False,
        exclude=True,
        description="Whether to include token usage information into instruction messages",
    )
    response_obj: BaseModel | None = Field(None, exclude=True)

    @model_validator(mode="after")
    def _validate_streaming(self) -> Self:
        if self.payload.get("stream") is True:
            self.streaming = True

        if self.include_token_usage_to_model and self.endpoint.requires_tokens:
            if isinstance(self.payload["messages"][-1], dict):
                required_tokens = self.required_tokens
                content = self.payload["messages"][-1]["content"]
                token_msg = (
                    f"\n\nEstimated Current Token Usage: {required_tokens}"
                )

                if "model" in self.payload:
                    if (
                        self.payload["model"].startswith("gpt-4")
                        or "o1mini" in self.payload["model"]
                        or "o1-preview" in self.payload["model"]
                    ):
                        token_msg += "/128_000"
                    elif "o1" in self.payload["model"]:
                        token_msg += "/200_000"
                    elif "sonnet" in self.payload["model"]:
                        token_msg += "/200_000"
                    elif "haiku" in self.payload["model"]:
                        token_msg += "/200_000"
                    elif "gemini" in self.payload["model"]:
                        token_msg += "/1_000_000"
                    elif "qwen-turbo" in self.payload["model"]:
                        token_msg += "/1_000_000"

                if isinstance(content, str):
                    content += token_msg
                elif isinstance(content, dict):
                    if "text" in content:
                        content["text"] += token_msg
                elif isinstance(content, list):
                    for i in reversed(content):
                        if "text" in i:
                            i["text"] += token_msg
                            break
                self.payload["messages"][-1]["content"] = content

        return self

    @property
    def required_tokens(self) -> int | None:
        """int | None: The number of tokens required for this request."""
        if self.endpoint.requires_tokens:
            return self.endpoint.calculate_tokens(self.payload)
        return None

    async def _inner(self, **kwargs) -> Any:
        """
        Performs the actual HTTP call using aiohttp, ignoring caching logic.

        - Retries on RateLimitError up to 3 times.
        - Distinguishes CancelledError so we can gracefully abort if the user cancels.

        Raises:
            ValueError: If required endpoint parameters are missing.
            RateLimitError: If repeated 'Rate limit' errors encountered.
            ExecutionError: For other API call failures.
            asyncio.CancelledError: If the operation is cancelled externally.
        """
        if not self.endpoint.required_kwargs.issubset(
            set(self.payload.keys())
        ):
            raise ValueError(
                f"Required kwargs not provided: {self.endpoint.required_kwargs}"
            )

        for k in list(self.payload.keys()):
            if k not in self.endpoint.acceptable_kwargs:
                self.payload.pop(k)

        async def retry_in():
            async with aiohttp.ClientSession() as session:
                try:
                    method_func = getattr(session, self.endpoint.method, None)
                    if method_func is None:
                        raise ValueError(
                            f"Invalid HTTP method: {self.endpoint.method}"
                        )
                    async with method_func(
                        self.endpoint.full_url, **kwargs
                    ) as response:
                        response_json = await response.json()

                        if "error" not in response_json:
                            return response_json

                        # Check for rate limit
                        if "Rate limit" in response_json["error"].get(
                            "message", ""
                        ):
                            await asyncio.sleep(5)
                            raise RateLimitError(
                                f"Rate limit exceeded: {response_json['error']}"
                            )
                        # Otherwise some other error
                        raise ExecutionError(
                            f"API call failed with error: {response_json['error']}"
                        )

                except asyncio.CancelledError:
                    # Gracefully handle user cancellation
                    logging.warning("API call canceled by external request.")
                    raise  # re-raise so caller knows it was cancelled

                except aiohttp.ClientError as e:
                    logging.error(f"API call failed: {e}")
                    # Return None or raise ExecutionError? Keep consistent
                    return None

        # Attempt up to 3 times if RateLimitError
        for i in range(3):
            try:
                return await retry_in()
            except asyncio.CancelledError:
                # On cancel, just re-raise
                raise
            except RateLimitError as e:
                if i == 2:
                    raise e
                wait = 2 ** (i + 1) * 0.5
                logging.warning(f"RateLimitError: {e}, retrying in {wait}s.")
                await asyncio.sleep(wait)

    @cached(**Settings.API.CACHED_CONFIG)
    async def _cached_inner(self, **kwargs) -> Any:
        """Cached version of `_inner` using aiocache.

        Args:
            **kwargs: Passed to `_inner`.

        Returns:
            Any: The result of `_inner`, possibly from cache.
        """
        return await self._inner(**kwargs)

    async def _stream(
        self,
        verbose: bool = True,
        output_file: str = None,
        with_response_header: bool = False,
    ) -> AsyncGenerator:
        async with aiohttp.ClientSession() as client:
            async with client.request(
                method=self.endpoint.method.upper(),
                url=self.endpoint.full_url,
                headers=self.headers,
                json=self.payload,
            ) as response:
                if response.status != 200:
                    try:
                        error_text = await response.json()
                    except Exception:
                        error_text = await response.text()
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"{error_text}",
                        headers=response.headers,
                    )

                file_handle = None

                if output_file:
                    try:
                        file_handle = open(output_file, "w")
                    except Exception as e:
                        raise ValueError(
                            f"Invalid to output the response "
                            f"to {output_file}. Error:{e}"
                        )

                try:
                    async for chunk in response.content:
                        chunk_str = chunk.decode("utf-8")
                        chunk_list = chunk_str.split("data:")
                        for c in chunk_list:
                            c = c.strip()
                            if c and c != "[DONE]":
                                try:
                                    if file_handle:
                                        file_handle.write(c + "\n")
                                    c_dict = json.loads(c)
                                    if verbose:
                                        if c_dict.get("choices"):
                                            if content := c_dict["choices"][0][
                                                "delta"
                                            ].get("content"):
                                                print(
                                                    content, end="", flush=True
                                                )
                                    yield c_dict
                                except json.JSONDecodeError:
                                    yield c
                                except asyncio.CancelledError as e:
                                    raise e

                    if with_response_header:
                        yield response.headers

                finally:
                    if file_handle:
                        file_handle.close()

    async def stream(
        self,
        verbose: bool = True,
        output_file: str = None,
        with_response_header: bool = False,
        **kwargs,
    ) -> AsyncGenerator:
        """Performs a streaming request, if supported by the endpoint.

        Args:
            verbose (bool):
                If True, prints the response content to the console.
            output_file (str):
                If set, writes the response content to this file. (only applies to non-endpoint invoke)
            with_response_header (bool):
                If True, yields the response headers as well. (only applies to non-endpoint invoke)
            **kwargs: Additional parameters for the streaming call.

        Yields:
            The streamed chunks of data, if any.

        Raises:
            ValueError: If the endpoint does not support streaming.
        """
        start = asyncio.get_event_loop().time()
        response = []
        e1 = None
        try:
            if self.should_invoke_endpoint and self.endpoint.is_streamable:
                async for i in self.endpoint._stream(
                    self.payload, self.headers, **kwargs
                ):
                    content = i.choices[0].delta.content
                    if verbose:
                        if content is not None:
                            print(content, end="", flush=True)
                    response.append(i)
                    yield i
            else:
                async for i in self._stream(
                    verbose=verbose,
                    output_file=output_file,
                    with_response_header=with_response_header,
                ):
                    response.append(i)
                    yield i
        except Exception as e:
            e1 = e
        finally:
            self.execution.duration = asyncio.get_event_loop().time() - start
            if not response and e1:
                self.execution.error = str(e1)
                self.execution.status = EventStatus.FAILED
                logging.error(
                    f"API call to {self.endpoint.full_url} failed: {e1}"
                )
            else:
                self.execution.response = response
                self.execution.status = EventStatus.COMPLETED

    async def invoke(self) -> None:
        """Invokes the API call, updating the execution state with results.

        Raises:
            Exception: If any error occurs, the status is set to FAILED and
                the error is logged.
        """
        start = asyncio.get_event_loop().time()
        kwargs = {"headers": self.headers, "json": self.payload}
        response = None
        e1 = None

        try:
            if self.should_invoke_endpoint and self.endpoint.is_invokeable:
                response = await self.endpoint.invoke(
                    payload=self.payload,
                    headers=self.headers,
                    is_cached=self.is_cached,
                )
            else:
                if self.is_cached:
                    response = await self._cached_inner(**kwargs)
                else:
                    response = await self._inner(**kwargs)

        except asyncio.CancelledError as ce:
            e1 = ce
            logging.warning("invoke() canceled by external request.")
            raise
        except Exception as ex:
            e1 = ex

        finally:
            self.execution.duration = asyncio.get_event_loop().time() - start
            if not response and e1:
                self.execution.error = str(e1)
                self.execution.status = EventStatus.FAILED
                logging.error(
                    f"API call to {self.endpoint.full_url} failed: {e1}"
                )
            else:
                self.response_obj = response
                self.execution.response = (
                    response.model_dump()
                    if isinstance(response, BaseModel)
                    else response
                )
                self.execution.status = EventStatus.COMPLETED

    def __str__(self) -> str:
        return (
            f"APICalling(id={self.id}, status={self.status}, duration="
            f"{self.execution.duration}, response={self.execution.response}"
            f", error={self.execution.error})"
        )

    __repr__ = __str__

    @property
    def request(self) -> dict:
        """dict: A partial dictionary with data about the request (e.g. tokens).

        Returns:
            dict: Contains 'required_tokens' if applicable.
        """
        return {
            "required_tokens": self.required_tokens,
        }

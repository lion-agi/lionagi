from typing import Any
import re

"""Provides functions for making API calls with retry and caching capabilities."""

import logging
import asyncio
from typing import Any, Callable

import aiohttp
from aiocache import cached

from lion_core import LN_UNDEFINED
from lion_core.libs import rcall
from lion_core.exceptions import LionOperationError
from lionagi.os.service.config import CACHED_CONFIG


async def call_api(
    http_session: aiohttp.ClientSession,
    url: str,
    method: str = "post",
    *,
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0,
    backoff_factor: float = 1,
    default: Any = LN_UNDEFINED,
    timeout: float | None = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: str | None = None,
    error_map: dict[type, Callable[[Exception], Any]] | None = None,
    **kwargs: Any,
) -> dict:
    """Make an API call with retry and error handling capabilities.

    Args:
        http_session: The aiohttp client session.
        url: The URL for the API call.
        method: The HTTP method to use (default: "post").
        retries: Number of retries for failed calls.
        initial_delay: Initial delay before first retry.
        delay: Delay between retries.
        backoff_factor: Factor to increase delay between retries.
        default: Default value to return on failure.
        timeout: Timeout for the API call.
        timing: Whether to time the API call.
        verbose: Whether to log verbose output.
        error_msg: Custom error message for failures.
        error_map: Mapping of exception types to handler functions.
        **kwargs: Additional keyword arguments for the API call.

    Returns:
        The API response or the default value on failure.
    """

    async def _api_call() -> dict | None:
        try:
            if (_m := getattr(http_session, method, None)) is not None:
                async with _m(url, **kwargs) as response:
                    response.raise_for_status()
                    response_json = await response.json()
                    if "error" not in response_json:
                        return response_json
                    if "Rate limit" in response_json["error"].get("message", ""):
                        await asyncio.sleep(15)
                    raise LionOperationError(
                        "API call failed with error: ", response_json["error"]
                    )
            else:
                raise ValueError(f"Invalid HTTP method: {method}")
        except aiohttp.ClientError as e:
            logging.error(f"API call to {url} failed: {e}")
            return None

    return await rcall(
        func=_api_call,
        retries=retries,
        initial_delay=initial_delay,
        delay=delay,
        backoff_factor=backoff_factor,
        default=default,
        timeout=timeout,
        timing=timing,
        verbose=verbose,
        error_msg=error_msg,
        error_map=error_map,
    )


@cached(**CACHED_CONFIG)
async def cached_call_api(
    http_session: aiohttp.ClientSession,
    url: str,
    method: str = "post",
    *,
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0,
    backoff_factor: float = 1,
    default: Any = LN_UNDEFINED,
    timeout: float | None = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: str | None = None,
    error_map: dict[type, Callable[[Exception], Any]] | None = None,
    **kwargs: Any,
) -> dict:
    """Make a cached API call with retry and error handling capabilities.

    This function wraps call_api with caching functionality.

    Args and Returns:
        See call_api function for details.
    """
    return await call_api(
        http_session=http_session,
        url=url,
        method=method,
        retries=retries,
        initial_delay=initial_delay,
        delay=delay,
        backoff_factor=backoff_factor,
        default=default,
        timeout=timeout,
        timing=timing,
        verbose=verbose,
        error_msg=error_msg,
        error_map=error_map,
        **kwargs,
    )


def api_endpoint_from_url(request_url: str) -> str:
    match = re.search(r"^https://[^/]+(/.+)?/v\d+/(.+)$", request_url)
    return match[2] if match else ""


def create_payload(
    input_: Any,
    config: dict,
    required_: list | tuple,
    optional_: list | tuple,
    input_key: str,
    **kwargs,
):
    config = {**config, **kwargs}
    payload = {input_key: input_}

    for key in required_:
        payload[key] = config[key]

    for key in optional_:
        if bool(config[key]) and str(config[key]).strip().lower() != "none":
            payload[key] = config[key]

    return payload


import aiohttp
from pydantic import Field, field_validator

from lion_core.abc import Action
from lion_core.generic.component import Component
from lion_core.generic.note import Note
from lion_core.exceptions import (
    LionValueError,
    LionResourceError,
    LionOperationError,
)
from lion_core.libs import to_dict
from lion_core.action.status import ActionStatus


class APICalling(Component, Action):

    name: str | None = Field("API Calling")
    content: Note = Field(default_factory=Note)
    status: ActionStatus = Field(ActionStatus.PENDING)

    def __init__(
        self,
        payload: dict = None,
        base_url: str = None,
        endpoint: str = None,
        api_key: str = None,
        method="post",
        content=None,
        required_tokens=15,
    ):
        if not content:
            content = Note()

        super().__init__(content=content)

        content_ = {
            "method": method,
            "payload": payload,
            "base_url": base_url,
            "endpoint": endpoint,
            "required_tokens": required_tokens,
        }

        for k, v in content_.items():
            if self.content.get(k, None) is None:
                self.content.set([k], v)

        if api_key is not None:
            self.content.set(["headers"], {"Authorization": f"Bearer {api_key}"})

    @field_validator("status", mode="before")
    def _validate_status(cls, value):
        if isinstance(value, ActionStatus):
            return value
        try:
            return ActionStatus(value)
        except:
            raise LionValueError(
                f"Invalid value: status must be one of {ActionStatus.__members__.keys()}"
            )

    async def invoke(self):
        with aiohttp.ClientSession() as session:
            try:
                method = self.content.get(["method"])
                if (_m := getattr(session, method, None)) is not None:

                    async with _m(
                        url=self.content.get(["base_url"])
                        + self.content.get(["endpoint"]),
                        headers=self.content.get(["headers"]),
                        json=self.content.get(["payload"]),
                    ) as response:

                        self.status = ActionStatus.PROCESSING
                        response_json = await response.json()
                        self.content.set(["response"], response_json)
                        self.content.pop(["headers"])

                        if "error" not in response_json:
                            return

                        if "error" in response_json:
                            self.status = ActionStatus.FAILED
                            self.content.set(["error"], response_json["error"])
                            raise LionOperationError(
                                "API call failed with error: ", response_json["error"]
                            )

                        if "Rate limit" in response_json["error"].get("message", ""):
                            self.status = ActionStatus.FAILED
                            self.content.set(["error"], response_json["error"])
                            raise LionResourceError(
                                f"Rate limit exceeded. Error: {response_json['error']}"
                            )
                else:
                    self.content.pop(["headers"])
                    self.status = ActionStatus.FAILED
                    self.content.set(["error"], f"Invalid HTTP method: {method}")
                    raise LionValueError(f"Invalid HTTP method: {method}")

            except aiohttp.ClientError as e:
                self.status = ActionStatus.FAILED
                self.content.pop(["headers"])
                self.content.set(["error"], f"API call failed: {e}")
                raise LionOperationError(f"API call failed: {e}")

    def to_dict(self):
        dict_ = super().to_dict()
        dict_["content"] = self.content.to_dict()
        if "headers" in dict_["content"]:
            dict_["content"].pop("headers")
        return dict_

    @classmethod
    def from_dict(cls, dict_: dict):
        dict_["content"] = Note(**to_dict(dict_.get("content", {})))
        return cls.from_dict(dict_)

# File: lionagi/os/service/api/utils.py

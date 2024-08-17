import re
import logging
import asyncio
from typing import Any, Callable

import aiohttp
from aiocache import cached

from lion_core.setting import LN_UNDEFINED
from lion_core.exceptions import LionOperationError, LionResourceError

from lionagi.os.libs import rcall
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
                        raise LionResourceError(
                            f"Rate limit exceeded. Error: {response_json['error']}"
                        )
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

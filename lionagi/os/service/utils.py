import re
import logging
from typing import Any

import aiohttp
from aiocache import cached
from lion_core.exceptions import LionOperationError, LionResourceError

from lionagi.os.libs import rcall
from lionagi.os.service.config import RetryConfig, DEFAULT_CACHED_CONFIG


async def call_api(
    http_session: aiohttp.ClientSession,
    url: str,
    method: str = "post",
    *,
    retry_config: RetryConfig | None = RetryConfig(),
    **kwargs: Any,  # additional kwargs for retry and api call
) -> dict:

    retry_config = retry_config.update(new_schema_obj=True, **kwargs)
    _config = {}
    for i in list(kwargs.keys()):
        if i not in retry_config.schema_keys():
            _config[i] = kwargs[i]

    async def _api_call() -> dict | None:
        try:
            if (_m := getattr(http_session, method, None)) is not None:
                async with _m(url, **_config) as response:
                    response_json = await response.json()
                    if "error" not in response_json:
                        return response_json
                    if "Rate limit" in response_json["error"].get("message", ""):
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

    return await rcall(func=_api_call, **retry_config.to_dict())


@cached(**DEFAULT_CACHED_CONFIG.to_dict())
async def cached_call_api(
    http_session: aiohttp.ClientSession,
    url: str,
    method: str = "post",
    *,
    retry_config: RetryConfig | None = RetryConfig(),
    **kwargs: Any,  # additional kwargs for retry and api call
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
        retry_config=retry_config,
        **kwargs,
    )


def api_endpoint_from_url(request_url: str) -> str:
    match = re.search(r"^https://[^/]+(/.+)?/v\d+/(.+)$", request_url)
    return match[2] if match else ""


def create_payload(
    payload_input: Any,
    payload_config: dict,
    required_params: list | tuple,
    optional_params: list | tuple,
    payload_input_key: str,
    **kwargs,
):
    payload_config = {**payload_config, **kwargs}
    payload = {payload_input_key: payload_input}

    for key in required_params:
        payload[key] = payload_config[key]

    for key in optional_params:
        if (
            bool(payload_config[key])
            and str(payload_config[key]).strip().lower() != "none"
        ):
            payload[key] = payload_config[key]

    return payload

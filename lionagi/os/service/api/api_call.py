import aiohttp
from aiocache import cached
from typing import Any, Callable
from lionagi import logging
from lion_core import LN_UNDEFINED
from lion_core.libs import rcall
from .utils import CACHED_CONFIG


async def api_call(
    http_session: aiohttp.ClientSession,
    url: str,
    method="post",
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
    **kwargs,
) -> Any:
    async def _api_call():
        try:
            if (_m := getattr(http_session, method, None)) is not None:
                async with _m(url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()
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
async def cached_api_call(
    http_session: aiohttp.ClientSession,
    url: str,
    method="post",
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
    **kwargs,
) -> Any:
    return await api_call(
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

import asyncio
from typing import Any, Type, Callable, Mapping
import logging
import aiohttp
from aiocache import cached
from functools import lru_cache
import re


@lru_cache(maxsize=None)
def api_endpoint_from_url(request_url: str) -> str:
    match = re.search(r"^https://[^/]+(/.+)?/v\d+/(.+)$", request_url)
    return match[2] if match else ""

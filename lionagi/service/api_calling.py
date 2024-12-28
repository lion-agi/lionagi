import asyncio
import logging
from typing import Any

import aiohttp
from aiocache import cached
from pydantic import Field, field_validator

from .._errors import ExecutionError, RateLimitError
from ..protocols.generic import Event, EventStatus, Execution
from ..settings import Settings
from ..utils import RCallParams
from .endpoint import EndPoint


class APICalling(Event):

    payload: dict
    headers: dict
    endpoint: EndPoint = Field(exclude=True)
    cached: bool = Field(default=False)
    rcall_params: RCallParams | None = Field(default=None, exclude=True)

    @field_validator("rcall_params", mode="before")
    def _validate_rcall_params(cls, value: Any) -> Any:
        if value is not None:
            if isinstance(value, dict):
                return RCallParams(**value)
            elif isinstance(value, RCallParams):
                return value
        return RCallParams()

    @property
    def required_tokens(self) -> int | None:
        return self.endpoint.calculate_tokens(self.payload)

    async def invoke(self):
        start = asyncio.get_event_loop().time()
        kwargs = {"headers": self.headers, "json": self.payload}

        async def _inner():
            if not self.endpoint.required_kwargs.issubset(
                set(self.payload.keys())
            ):
                raise ValueError(
                    f"Required kwargs not fully provided: {self.endpoint.required_kwargs}"
                )
            if self.endpoint.optional_kwargs and any(
                i not in j
                for j in self.endpoint.acceptable_kwargs
                for i in self.payload.keys()
            ):
                raise ValueError(
                    f"Extra kwargs detected and some are not allowed: {self.endpoint.optional_kwargs}"
                )
            async with aiohttp.ClientSession() as session:
                try:
                    if (
                        _m := getattr(session, self.endpoint.method, None)
                    ) is not None:
                        async with _m(
                            self.endpoint.full_url, **kwargs
                        ) as response:
                            response_json = await response.json()
                            if "error" not in response_json:
                                return response_json
                            if "Rate limit" in response_json["error"].get(
                                "message", ""
                            ):
                                await asyncio.sleep(5)
                                raise RateLimitError(
                                    f"Rate limit exceeded. Error: {response_json['error']}"
                                )
                            raise ExecutionError(
                                "API call failed with error: ",
                                response_json["error"],
                            )
                    else:
                        raise ValueError(f"Invalid HTTP method: {self.method}")
                except aiohttp.ClientError as e:
                    logging.error(f"API call to {self.full_url} failed: {e}")
                    return None

        @cached(**Settings.Action.CACHED_CONFIG)
        async def _cached_inner():
            return await _inner()

        try:
            response = None
            if self.endpoint.is_invokeable():
                response = await self.rcall_params(
                    self.endpoint.invoke,
                    payload=self.payload,
                    headers=self.headers,
                    cached=self.cached,
                )
            else:
                if self.cached:
                    response = await self.rcall_params(_cached_inner)
                else:
                    response = await self.rcall_params(_inner)
            self.execution = Execution(
                status=EventStatus.COMPLETED,
                duration=asyncio.get_event_loop().time() - start,
                response=response,
            )
        except Exception as e:
            self.execution = Execution(
                status=EventStatus.FAILED,
                duration=asyncio.get_event_loop().time() - start,
                response=None,
                error=str(e),
            )
            logging.error(f"API call to {self.endpoint.full_url} failed: {e}")

    def to_dict(self) -> dict:
        dict_ = super().to_dict()
        headers = self.headers.copy()
        if "Authorization" in headers:
            headers["Authorization"] = (
                f"Bearer ****{headers['Authorization'][-4:]}"
            )
        dict_["headers"] = headers
        dict_["cached"] = self.cached
        return dict_

    def __str__(self) -> str:
        return f"APICalling(id={self.id}, status={self.status}, duration={self.execution.duration}, response={self.execution.response}, error={self.execution.error})"

    __repr__ = __str__

    @property
    def request(self) -> dict:
        return {
            "required_tokens": self.required_tokens,
        }

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

import aiohttp
from aiocache import cached
from pydantic import BaseModel, Field

from lionagi._errors import ExecutionError, RateLimitError
from lionagi.protocols.generic.event import EventStatus
from lionagi.settings import Settings

from .base import ConnectionEvent, Connector, ConnectorConfig



class RESTHeaders(BaseModel):
    
    pass


class RESTConnectorConfig(ConnectorConfig):
    """
    REST Connector config for the endpoint.
    """

    base_url: str | None = Field(
        None,
        description="The base url of the endpoint.",
    )
    endpoint: str | None = Field(
        None,
        description="The endpoint of the endpoint.",
    )
    path_params: list | None = Field(
        None,
        description="The path params of the endpoint.",
    )
    method: str | None = Field(
        None,
        description="The method of the endpoint.",
    )
    header_schema: dict | None = Field(
        None,
        description="The headers of the endpoint.",
    )
    requires_auth: bool | None = Field(
        None,
        description="Whether the endpoint requires authentication.",
    )
    request_schema: dict | None = Field(
        None,
        description="The request schema of the endpoint.",
    )


    def full_url(self, **kwargs) -> str:
        """str: The complete URL, including base_url and any parameters."""
        url_ = (
            self.base_url
            if self.base_url.endswith("/")
            else self.base_url + "/"
        )

        if self.path_params:
            for k in self.path_params:
                if k not in kwargs:
                    raise ValueError(f"Missing required path parameter: {k}")
            return url_ + self.endpoint.format(
                **{k: v for k, v in kwargs.items() if k in self.path_params}
            )

        return url_ + self.endpoint

    @property
    def acceptable_fields(self) -> set[str]:
        """set[str]: All parameters that are not explicitly prohibited."""
        return set(self.required_fields + self.optional_fields)


class RESTConnector(Connector):

    def __init__(self, config: RESTConnectorConfig):
        super().__init__()
        self.config: RESTConnectorConfig = config

    async def _inner(self, **kwargs) -> Any:
        if not set(self.config.required_fields).issubset(
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

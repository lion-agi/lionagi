# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import re
from collections.abc import AsyncGenerator
from os import getenv
from typing import Any

import aiohttp
from pydantic import BaseModel, Field, field_validator

from .data_models import (
    GroqEndpointPathParam,
    GroqEndpointQueryParam,
    GroqEndpointRequestBody,
)
from .response_utils import match_response

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_TIMEOUT = 30  # seconds


class GroqRequest(BaseModel):
    api_key: str = Field(
        description="API key for authentication", exclude=True
    )
    endpoint: str = Field(description="API endpoint")
    method: str = Field(description="HTTP method")
    content_type: str | None = Field(
        default="application/json", description="Content type for the request"
    )
    timeout: float = Field(
        default=DEFAULT_TIMEOUT,
        description="Request timeout in seconds",
        ge=0,
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "allow",  # Allow extra attributes for mocking
    }

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        # First try to get from env if v looks like an env var
        if re.match(r"^[A-Z_][A-Z0-9_]*$", v):
            env_value = getenv(v)
            if env_value:
                v = env_value

        # Validate key format
        if not v.startswith(("groq_", "gsk_")):
            raise ValueError("Invalid Groq API key format")
        return v

    def get_headers(self) -> dict[str, str]:
        """Get headers for the request."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        if self.content_type:
            headers["Content-Type"] = self.content_type
        return headers

    def get_endpoint(
        self, path_param: GroqEndpointPathParam | None = None
    ) -> str:
        """Get the formatted endpoint URL."""
        endpoint = self.endpoint
        if path_param:
            try:
                endpoint = endpoint.format(**path_param.model_dump())
            except KeyError as e:
                raise ValueError(f"Missing path parameter: {e}")
        return f"{GROQ_BASE_URL}/{endpoint}"

    async def invoke(
        self,
        request_body: GroqEndpointRequestBody | None = None,
        params: GroqEndpointQueryParam | None = None,
        form_data: dict[str, Any] | None = None,
        path_param: GroqEndpointPathParam | None = None,
        output_file: str | None = None,
        with_response_header: bool = False,
        parse_response: bool = True,
        **kwargs,
    ) -> Any:
        """Make a request to the Groq API."""
        url = self.get_endpoint(path_param)
        headers = self.get_headers()
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        # Convert Pydantic models to dict
        json_data = (
            request_body.model_dump(exclude_unset=True)
            if request_body
            else None
        )
        params = params.model_dump(exclude_unset=True) if params else None

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if form_data:
                    data = aiohttp.FormData()
                    for key, value in form_data.items():
                        data.add_field(key, value)
                    async with session.request(
                        self.method,
                        url,
                        headers=headers,
                        data=data,
                        params=params,
                    ) as response:
                        return await self._handle_response(
                            response,
                            output_file,
                            with_response_header,
                            parse_response,
                        )
                else:
                    async with session.request(
                        self.method,
                        url,
                        headers=headers,
                        json=json_data,
                        params=params,
                    ) as response:
                        return await self._handle_response(
                            response,
                            output_file,
                            with_response_header,
                            parse_response,
                        )
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to connect to Groq API: {str(e)}")
        except TimeoutError:
            raise TimeoutError(
                f"Request timed out after {self.timeout} seconds"
            )

    async def stream(
        self,
        request_body: GroqEndpointRequestBody | None = None,
        output_file: str | None = None,
        with_response_header: bool = False,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream response from the Groq API."""
        if request_body and not getattr(request_body, "stream", False):
            raise ValueError(
                "Request does not support stream. "
                "Only requests with stream=True are supported"
            )

        url = self.get_endpoint()
        headers = self.get_headers()
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        # Convert Pydantic model to dict
        json_data = (
            request_body.model_dump(exclude_unset=True)
            if request_body
            else None
        )

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    self.method, url, headers=headers, json=json_data
                ) as response:
                    if response.status != 200:
                        error_text = await self._get_error_text(response)
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=error_text,
                            headers=response.headers,
                        )

                    file_handle = None
                    if output_file:
                        try:
                            file_handle = open(output_file, "w")
                        except Exception as e:
                            raise ValueError(
                                f"Failed to open output file {output_file}: {str(e)}"
                            )

                    try:
                        async for line in response.content:
                            if line:
                                try:
                                    line = line.decode("utf-8").strip()
                                except UnicodeDecodeError:
                                    import warnings

                                    warnings.warn(
                                        "Failed to decode response chunk"
                                    )
                                    continue

                                if line.startswith("data: "):
                                    line = line[6:]  # Remove "data: " prefix

                                if line == "[DONE]":
                                    break

                                try:
                                    chunk_data = json.loads(line)
                                    if file_handle:
                                        file_handle.write(
                                            json.dumps(chunk_data) + "\n"
                                        )
                                    yield chunk_data
                                except json.JSONDecodeError:
                                    import warnings

                                    warnings.warn(
                                        f"Failed to parse response chunk: {line}"
                                    )
                                    continue

                        if with_response_header:
                            yield dict(response.headers)
                    finally:
                        if file_handle:
                            file_handle.close()

        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to connect to Groq API: {str(e)}")
        except TimeoutError:
            raise TimeoutError(
                f"Stream timed out after {self.timeout} seconds"
            )

    async def _handle_response(
        self,
        response: aiohttp.ClientResponse,
        output_file: str | None = None,
        with_response_header: bool = False,
        parse_response: bool = True,
    ) -> Any:
        """Handle the API response."""
        if response.status != 200:
            error_text = await self._get_error_text(response)
            raise aiohttp.ClientResponseError(
                request_info=response.request_info,
                history=response.history,
                status=response.status,
                message=error_text,
                headers=response.headers,
            )

        if output_file:
            with open(output_file, "wb") as f:
                async for chunk in response.content.iter_chunked(1024):
                    f.write(chunk)
            return None

        response_body = await response.json()

        if parse_response:
            response_body = match_response(self, response_body)

        if with_response_header:
            return response_body, dict(response.headers)
        return response_body

    async def _get_error_text(self, response: aiohttp.ClientResponse) -> str:
        """Extract error text from response."""
        try:
            error_json = await response.json()
            return json.dumps(error_json)
        except Exception:
            try:
                return await response.text()
            except Exception:
                return f"HTTP {response.status}"

    def __repr__(self):
        return (
            f"GroqRequest(endpoint={self.endpoint}, method={self.method}, "
            f"content_type={self.content_type})"
        )

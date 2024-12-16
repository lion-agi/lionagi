import json
from collections.abc import AsyncGenerator
from typing import Any, Dict, Optional, Tuple, Union

import aiohttp
from pydantic import BaseModel, ConfigDict, Field

from lionagi.integrations.perplexity_.api_endpoints.data_models import (
    PerplexityEndpointRequestBody,
)


class PerplexityRequest(BaseModel):
    """Handler for making requests to the Perplexity API."""

    api_key: str = Field(
        description="API key for authentication", exclude=True
    )
    endpoint: str = Field(description="Endpoint for request")
    method: str = Field(description="HTTP method")
    content_type: str | None = "application/json"
    base_url: str = "https://api.perplexity.ai"

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",  # Allow extra attributes for mocking in tests
    )

    async def invoke(
        self,
        json_data: None | (
            dict[str, Any] | PerplexityEndpointRequestBody
        ) = None,
        form_data: BaseModel | None = None,
        output_file: str | None = None,
        with_response_header: bool = False,
        parse_response: bool = True,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, str]] | bytes | None:
        """Make a request to the Perplexity API."""
        url = f"{self.base_url}/{self.endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        if self.content_type:
            headers["Content-Type"] = self.content_type

        if isinstance(json_data, PerplexityEndpointRequestBody):
            json_data = json_data.model_dump(exclude_unset=True)

        async with aiohttp.ClientSession() as client:
            response = await client.request(
                method=self.method,
                url=url,
                headers=headers,
                json=json_data,
                data=form_data.model_dump() if form_data else None,
            )
            async with response:
                if response.status != 200:
                    try:
                        error_body = await response.json()
                        error_msg = error_body.get("error", {}).get(
                            "message", str(error_body)
                        )
                    except Exception:
                        error_msg = await response.text()
                    raise Exception(
                        f"API request failed with status {response.status}: {error_msg}"
                    )

                if output_file:
                    with open(output_file, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    return None

                if parse_response:
                    response_body = await response.json()
                else:
                    response_body = await response.text()
                    try:
                        response_body = json.loads(response_body)
                    except json.JSONDecodeError:
                        pass

                if with_response_header:
                    headers = {
                        k.lower(): v for k, v in response.headers.items()
                    }
                    return response_body, headers
                return response_body

    async def stream(
        self,
        json_data: None | (
            dict[str, Any] | PerplexityEndpointRequestBody
        ) = None,
        output_file: str | None = None,
        with_response_header: bool = False,
        verbose: bool = True,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream responses from the Perplexity API."""
        if isinstance(json_data, PerplexityEndpointRequestBody):
            json_data = json_data.model_dump(exclude_unset=True)

        if not json_data.get("stream", False):
            json_data["stream"] = True

        url = f"{self.base_url}/{self.endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        async with aiohttp.ClientSession() as client:
            response = await client.post(url, headers=headers, json=json_data)
            async with response:
                if response.status != 200:
                    try:
                        error_body = await response.json()
                        error_msg = error_body.get("error", {}).get(
                            "message", str(error_body)
                        )
                    except Exception:
                        error_msg = await response.text()
                    raise Exception(
                        f"API request failed with status {response.status}: {error_msg}"
                    )

                if with_response_header:
                    headers = {
                        k.lower(): v for k, v in response.headers.items()
                    }
                    yield {"headers": headers}

                file_handle = None
                if output_file:
                    try:
                        file_handle = open(output_file, "w")
                    except Exception as e:
                        raise ValueError(
                            f"Failed to open output file {output_file}: {e}"
                        )

                try:
                    async for chunk in response.content:
                        if chunk:
                            chunk_str = chunk.decode("utf-8").strip()
                            if chunk_str.startswith("data: "):
                                chunk_str = chunk_str[
                                    6:
                                ]  # Remove "data: " prefix
                            try:
                                chunk_data = json.loads(chunk_str)
                                if file_handle:
                                    file_handle.write(
                                        json.dumps(chunk_data) + "\n"
                                    )
                                if verbose and "choices" in chunk_data:
                                    content = chunk_data["choices"][0][
                                        "delta"
                                    ]["content"]
                                    print(content, end="", flush=True)
                                yield chunk_data
                            except json.JSONDecodeError:
                                continue
                finally:
                    if file_handle:
                        file_handle.close()

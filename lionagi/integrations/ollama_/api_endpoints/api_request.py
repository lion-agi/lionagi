# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import json

import aiohttp
from pydantic import BaseModel, Field

from .data_models import OllamaEndpointRequestBody
from .match_response import match_response


class OllamaRequest(BaseModel):
    endpoint: str = Field(description="Endpoint for request")

    method: str = Field(description="HTTP method")

    @property
    def base_url(self):
        return "http://localhost:11434/api/"

    async def invoke(
        self,
        json_data: OllamaEndpointRequestBody = None,
        output_file: str = None,
        with_response_header: bool = False,
        parse_response: bool = True,
    ):
        url = self.base_url + self.endpoint
        json_data = (
            json_data.model_dump(exclude_unset=True) if json_data else None
        )

        async with aiohttp.ClientSession() as client:
            async with client.request(
                method=self.method, url=url, json=json_data
            ) as response:
                if response.status != 200:
                    try:
                        error_text = await response.json()
                    except:
                        error_text = await response.text()
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"HTTP Error {response.status}. Response Body: {error_text}",
                        headers=response.headers,
                    )

                # handle stream
                if (
                    response.headers.get("Content-Type")
                    == "application/x-ndjson"
                ):
                    response_body = []
                    file_handle = None
                    if output_file:
                        try:
                            file_handle = open(output_file, "w")
                        except Exception as e:
                            raise ValueError(
                                f"Invalid to output the response to {output_file}. Error:{e}"
                            )
                    try:
                        async for chunk in response.content:
                            chunk_str = chunk.decode("utf-8")
                            chunk_str = chunk_str.strip()
                            response_body.append(json.loads(chunk_str))
                            if "status" in json.loads(chunk_str):
                                print(json.loads(chunk_str))
                            if file_handle:
                                file_handle.write(chunk_str + "\n")

                    finally:
                        if file_handle:
                            file_handle.close()

                    if parse_response:
                        response_body = match_response(self, response_body)
                    if with_response_header:
                        return response_body, response.headers
                    else:
                        return response_body
                else:
                    try:
                        response_body = await response.json()
                    except:
                        response_body = await response.text()

                    if output_file:
                        try:
                            with open(output_file, "wb") as f:
                                f.write(await response.read())
                        except Exception as e:
                            raise ValueError(
                                f"Invalid to output the response to {output_file}. Error:{e}"
                            )

                    if parse_response:
                        response_body = match_response(self, response_body)
                    if with_response_header:
                        return response_body, response.headers
                    else:
                        return response_body

    async def stream(
        self,
        json_data: OllamaEndpointRequestBody,
        verbose: bool = True,
        output_file: str = None,
        with_response_header: bool = False,
    ):

        if not getattr(json_data, "stream", None):
            raise ValueError(
                "Request does not support stream or is not in stream mode. "
                "Only requests with stream=True are supported."
            )

        url = self.base_url + self.endpoint
        json_data = json_data.model_dump(exclude_unset=True)

        async with aiohttp.ClientSession() as client:
            async with client.request(
                method=self.method, url=url, json=json_data
            ) as response:
                if response.status != 200:
                    try:
                        error_text = await response.json()
                    except:
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
                            f"Invalid to output the response to {output_file}. Error:{e}"
                        )

                try:
                    async for chunk in response.content:
                        chunk_str = chunk.decode("utf-8")
                        chunk_str = chunk_str.strip()
                        if file_handle:
                            file_handle.write(chunk_str + "\n")

                        chunk_dict = json.loads(chunk_str)
                        if verbose:
                            if chunk_dict.get("response"):
                                print(
                                    chunk_dict.get("response"),
                                    end="",
                                    flush=True,
                                )
                            if message := chunk_dict.get("message"):
                                print(
                                    message.get("content"), end="", flush=True
                                )

                        yield chunk_dict

                    if with_response_header:
                        yield response.headers

                finally:
                    if file_handle:
                        file_handle.close()

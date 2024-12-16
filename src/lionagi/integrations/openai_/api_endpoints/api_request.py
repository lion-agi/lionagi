import json
from io import IOBase
from os import getenv

import aiohttp
from pydantic import BaseModel, Field, field_validator

from .data_models import (
    OpenAIEndpointPathParam,
    OpenAIEndpointQueryParam,
    OpenAIEndpointRequestBody,
)
from .match_response import match_response


class OpenAIRequest(BaseModel):

    api_key: str = Field(
        description="API key for authentication", exclude=True
    )

    openai_organization: str | None = Field(
        default=None, description="Organization id", exclude=True
    )

    openai_project: str | None = Field(
        default=None, description="Project id", exclude=True
    )

    endpoint: str = Field(description="Endpoint for request")

    method: str = Field(description="HTTP method")

    content_type: str | None = Field(
        default=None, description="HTTP Content-Type"
    )

    @field_validator("api_key", "openai_organization", "openai_project")
    @classmethod
    def get_id(cls, value: str) -> str:
        try:
            if api_key := getenv(value):
                return api_key
            else:
                return value
        except Exception:
            return value

    def get_endpoint(self, path_param: OpenAIEndpointPathParam = None):
        if path_param is None:
            return self.endpoint
        else:
            return self.endpoint.format(**path_param.model_dump())

    @property
    def base_url(self):
        return "https://api.openai.com/v1/"

    async def invoke(
        self,
        json_data: OpenAIEndpointRequestBody = None,
        params: OpenAIEndpointQueryParam = None,
        form_data: OpenAIEndpointRequestBody = None,
        path_param: OpenAIEndpointPathParam = None,
        output_file: str = None,
        with_response_header: bool = False,
        parse_response: bool = True,
    ):
        def get_headers():
            header = {"Authorization": f"Bearer {self.api_key}"}
            if self.content_type:
                header["Content-Type"] = self.content_type
            if self.openai_organization:
                header["OpenAI-Organization"] = self.openai_organization
            if self.openai_project:
                header["OpenAI-Project"] = self.openai_project
            return header

        def parse_form_data(data: OpenAIEndpointRequestBody):
            form_data = aiohttp.FormData()
            # for field in data.model_fields:
            for field in data.model_dump(exclude_unset=True):
                if value := getattr(data, field):
                    if isinstance(value, IOBase):
                        form_data.add_field(field, getattr(data, field))
                    else:
                        form_data.add_field(field, str(getattr(data, field)))
            return form_data

        url = self.base_url + self.get_endpoint(path_param)
        headers = get_headers()
        json_data = (
            json_data.model_dump(exclude_unset=True) if json_data else None
        )
        params = params.model_dump(exclude_unset=True) if params else None
        form_data = parse_form_data(form_data) if form_data else None

        async with aiohttp.ClientSession() as client:
            async with client.request(
                method=self.method,
                url=url,
                headers=headers,
                json=json_data,
                params=params,
                data=form_data,
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

                # handle stream in chat completions
                if json_data:
                    if json_data.get("stream"):
                        response_body = []
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
                                    if c and "DONE" not in c:
                                        if file_handle:
                                            file_handle.write(c + "\n")
                                        response_body.append(json.loads(c))

                        finally:
                            if file_handle:
                                file_handle.close()

                        if parse_response:
                            response_body = match_response(self, response_body)
                        if with_response_header:
                            return response_body, response.headers
                        else:
                            return response_body

                if output_file:
                    try:
                        with open(output_file, "wb") as f:
                            f.write(await response.read())
                    except Exception as e:
                        raise ValueError(
                            f"Invalid to output the response "
                            f"to {output_file}. Error:{e}"
                        )
                if self.endpoint != "audio/speech":
                    if (
                        response.headers.get("Content-Type")
                        == "application/json"
                    ):
                        response_body = await response.json()
                    else:
                        response_body = await response.text()

                    if parse_response:
                        response_body = match_response(self, response_body)
                    if with_response_header:
                        return response_body, response.headers
                    else:
                        return response_body

                else:
                    if with_response_header:
                        return (
                            None,
                            response.headers,
                        )  # audio/speech has no response object
                    else:
                        return None

    async def stream(
        self,
        json_data: OpenAIEndpointRequestBody,
        verbose: bool = True,
        output_file: str = None,
        with_response_header: bool = False,
    ):
        # for Chat Completions API only
        if not getattr(json_data, "stream"):
            raise ValueError(
                "Request does not support stream. "
                "Only chat completions requests with stream=True are supported"
            )

        def get_headers():
            header = {"Authorization": f"Bearer {self.api_key}"}
            if self.content_type:
                header["Content-Type"] = self.content_type
            if self.openai_organization:
                header["OpenAI-Organization"] = self.openai_organization
            if self.openai_project:
                header["OpenAI-Project"] = self.openai_project
            return header

        url = self.base_url + self.get_endpoint()
        headers = get_headers()
        json_data = (
            json_data.model_dump(exclude_unset=True) if json_data else None
        )

        async with aiohttp.ClientSession() as client:
            async with client.request(
                method=self.method, url=url, headers=headers, json=json_data
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
                            if c and "DONE" not in c:
                                if file_handle:
                                    file_handle.write(c + "\n")
                                c_dict = json.loads(c)
                                if verbose:
                                    if c_dict.get("choices"):
                                        if content := c_dict["choices"][0][
                                            "delta"
                                        ].get("content"):
                                            print(content, end="", flush=True)
                                yield c_dict

                    if with_response_header:
                        yield response.headers

                finally:
                    if file_handle:
                        file_handle.close()

    def __repr__(self):
        return (
            f"OpenAIRequest(endpoint={self.endpoint}, method={self.method}, "
            f"content_type={self.content_type})"
        )

from os import getenv
import aiohttp
from pydantic import BaseModel, Field, field_validator

from .data_models import OpenAIEndpointRequestBody


class OpenAIRequest(BaseModel):

    api_key: str = Field(description="API key for authentication", exclude=True)

    openai_organization: str | None = Field(
        default=None, description="Organization id", exclude=True
    )

    openai_project: str | None = Field(
        default=None, description="Project id", exclude=True
    )

    endpoint: str = Field(description="Endpoint for request")

    method: str = Field(description="HTTP method")

    content_type: str | None = Field(default=None, description="HTTP Content-Type")

    @field_validator("api_key", "openai_organization", "openai_project")
    @classmethod
    def get_id(cls, value: str) -> str:
        if api_key := getenv(value):
            return api_key
        else:
            return value

    @property
    def base_url(self):
        return "https://api.openai.com/v1/"

    async def invoke(self, data: OpenAIEndpointRequestBody = None):
        def get_headers():
            header = {"Authorization": f"Bearer {self.api_key}"}
            if self.content_type:
                header["Content-Type"] = self.content_type
            if self.openai_organization:
                header["OpenAI-Organization"] = self.openai_organization
            if self.openai_project:
                header["OpenAI-Project"] = self.openai_project
            return header

        url = self.base_url + self.endpoint
        headers = get_headers()
        data = data.model_dump(exclude_unset=True) if data else None

        async with aiohttp.ClientSession() as client:
            async with client.request(
                method=self.method, url=url, headers=headers, json=data
            ) as response:
                response.raise_for_status()

                if response.headers.get("Content-Type") == "application/json":
                    response_headers = response.headers
                    response_body = await response.json()
                else:
                    response_headers = response.headers
                    response_body = await response.text()

                return response_body, response_headers

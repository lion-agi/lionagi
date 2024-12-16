from typing import List, Literal, Optional

from pydantic import Field

from ..data_models import OpenAIEndpointQueryParam, OpenAIEndpointResponseBody
from .file_models import OpenAIFileResponseBody


class OpenAIListFilesQueryParam(OpenAIEndpointQueryParam):
    purpose: str | None = Field(
        description="Only return files with the given purpose."
    )


class OpenAIListFilesResponseBody(OpenAIEndpointResponseBody):
    data: list[OpenAIFileResponseBody] = Field(
        description="The list of file objects."
    )

    object: Literal["list"] = Field(
        description='The object type, which is always "list".'
    )

    has_more: bool = Field(
        description="Whether there are more results"
        " available after this batch."
    )

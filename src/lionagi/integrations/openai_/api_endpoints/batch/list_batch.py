from typing import List, Literal, Optional

from pydantic import Field

from ..data_models import OpenAIEndpointQueryParam, OpenAIEndpointResponseBody
from .batch_models import OpenAIBatchResponseBody


class OpenAIListBatchQueryParam(OpenAIEndpointQueryParam):
    after: str | None = Field(
        None, description="A cursor for use in pagination. "
    )

    limit: int | None = Field(
        default=20,
        description="A limit on the number of objects to be returned. "
        "Limit can range between 1 and 100, and the default is 20.",
    )


class OpenAIListBatchResponseBody(OpenAIEndpointResponseBody):
    data: list[OpenAIBatchResponseBody] = Field(
        description="The list of batch objects."
    )

    object: Literal["list"] = Field(
        description='The object type, which is always "list".'
    )

    first_id: str = Field(description="The first object id in the list")

    last_id: str = Field(description="The last object id in the list")

    has_more: bool = Field(
        description="Whether there are more results "
        "available after this batch."
    )

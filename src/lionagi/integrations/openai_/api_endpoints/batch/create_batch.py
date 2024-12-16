from typing import Literal, Optional

from pydantic import Field

from ..data_models import OpenAIEndpointRequestBody
from .types import Endpoint


class OpenAIBatchRequestBody(OpenAIEndpointRequestBody):
    input_file_id: str = Field(
        description="The ID of an uploaded file that contains requests"
        " for the new batch."
    )

    endpoint: Endpoint = Field(
        description="The endpoint to be used for all requests in the batch."
    )

    completion_window: Literal["24h"] = Field(
        description="The time frame within which the batch"
        " should be processed."
    )

    metadata: dict | None = Field(
        None, description="Optional custom metadata for the batch."
    )

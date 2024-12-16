from typing import List, Literal, Optional

from pydantic import Field

from ..data_models import OpenAIEndpointQueryParam, OpenAIEndpointResponseBody
from .fine_tuning_job_models import OpenAIFineTuningJobResponseBody


class OpenAIListFineTuningJobsQueryParam(OpenAIEndpointQueryParam):
    after: str | None = Field(
        None,
        description="Identifier for the last job from the previous pagination request.",
    )

    limit: int | None = Field(
        20, description="Number of fine-tuning jobs to retrieve.", ge=1
    )


class OpenAIListFineTuningJobsResponseBody(OpenAIEndpointResponseBody):
    object: Literal["list"] = Field(
        description="The object type, always 'list' for a list of fine-tuning jobs.",
    )

    data: list[OpenAIFineTuningJobResponseBody] = Field(
        description="A list of fine-tuning job events."
    )

    has_more: bool = Field(
        description="Whether there are more results available after this batch."
    )

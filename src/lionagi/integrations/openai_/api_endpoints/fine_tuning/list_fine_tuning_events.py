from typing import List, Literal, Optional

from pydantic import Field

from ..data_models import (
    OpenAIEndpointPathParam,
    OpenAIEndpointQueryParam,
    OpenAIEndpointResponseBody,
)
from .fine_tuning_job_event_models import OpenAIFineTuningJobEventResponseBody


# Request model
class OpenAIListFineTuningEventsPathParam(OpenAIEndpointPathParam):
    fine_tuning_job_id: str = Field(
        description="The ID of the fine-tuning job to get events for."
    )


class OpenAIListFineTuningEventsQueryParam(OpenAIEndpointQueryParam):
    after: str | None = Field(
        None,
        description="Identifier for the last event from the previous pagination request.",
    )

    limit: int | None = Field(
        20, description="Number of events to retrieve.", ge=1
    )


class OpenAIListFineTuningEventsResponseBody(OpenAIEndpointResponseBody):
    object: Literal["list"] = Field(
        description="The object type, always 'list' for a list of fine-tuning events.",
    )

    data: list[OpenAIFineTuningJobEventResponseBody] = Field(
        description="A list of fine-tuning events."
    )

    has_more: bool = Field(
        description="Whether there are more results available after this batch."
    )

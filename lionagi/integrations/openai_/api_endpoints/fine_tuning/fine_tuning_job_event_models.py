from typing import Literal, Optional

from pydantic import Field

from ..data_models import OpenAIEndpointResponseBody


class OpenAIFineTuningJobEventResponseBody(OpenAIEndpointResponseBody):
    id: str = Field(description="The ID of the fine-tuning event.")

    created_at: int = Field(
        description="The Unix timestamp (in seconds) of when the event was created.",
    )

    level: str = Field(description="The level of the event (e.g., 'info').")

    object: Literal["fine_tuning.job.event"] = Field(
        "fine_tuning.job.event",
        description="The object type, always 'fine_tuning.job.event'.",
    )

    message: str = Field(
        ..., description="The message associated with the event."
    )

    # TODO: check Job Event Response
    data: dict | None = Field(
        None, description="Additional data associated with the event, if any."
    )

    type: str = Field(description="The type of the event (e.g., 'message').")

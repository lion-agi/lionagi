from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# Request model
class ListFineTuningEventsRequest(BaseModel):
    fine_tuning_job_id: str = Field(
        ..., description="The ID of the fine-tuning job to get events for."
    )
    after: Optional[str] = Field(
        None,
        description="Identifier for the last event from the previous pagination request.",
    )
    limit: Optional[int] = Field(20, description="Number of events to retrieve.", ge=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "fine_tuning_job_id": "ftjob-abc123",
                "after": "ft-event-123456",
                "limit": 10,
            }
        }
    )


# Response models
class FineTuningEvent(BaseModel):
    object: Literal["fine_tuning.job.event"] = Field(
        "fine_tuning.job.event",
        description="The object type, always 'fine_tuning.job.event'.",
    )
    id: str = Field(..., description="The ID of the fine-tuning event.")
    created_at: int = Field(
        ...,
        description="The Unix timestamp (in seconds) of when the event was created.",
    )
    level: str = Field(..., description="The level of the event (e.g., 'info').")
    message: str = Field(..., description="The message associated with the event.")
    data: Optional[dict] = Field(
        None, description="Additional data associated with the event, if any."
    )
    type: str = Field(..., description="The type of the event (e.g., 'message').")


class ListFineTuningEventsResponse(BaseModel):
    object: Literal["list"] = Field(
        "list",
        description="The object type, always 'list' for a list of fine-tuning events.",
    )
    data: List[FineTuningEvent] = Field(
        ..., description="A list of fine-tuning events."
    )
    has_more: bool = Field(
        ..., description="Whether there are more results available after this batch."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "object": "list",
                "data": [
                    {
                        "object": "fine_tuning.job.event",
                        "id": "ft-event-ddTJfwuMVpfLXseO0Am0Gqjm",
                        "created_at": 1721764800,
                        "level": "info",
                        "message": "Fine tuning job successfully completed",
                        "data": None,
                        "type": "message",
                    },
                    {
                        "object": "fine_tuning.job.event",
                        "id": "ft-event-tyiGuB72evQncpH87xe505Sv",
                        "created_at": 1721764800,
                        "level": "info",
                        "message": "New fine-tuned model created: ft:gpt-4o-mini:openai::7p4lURel",
                        "data": None,
                        "type": "message",
                    },
                ],
                "has_more": True,
            }
        }
    )

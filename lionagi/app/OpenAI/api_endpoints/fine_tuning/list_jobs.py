from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# Request model
class ListFineTuningJobsRequest(BaseModel):
    after: Optional[str] = Field(
        None,
        description="Identifier for the last job from the previous pagination request.",
    )
    limit: Optional[int] = Field(
        20, description="Number of fine-tuning jobs to retrieve.", ge=1
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"after": "ft-job-123456", "limit": 10}}
    )


# Response models
class FineTuningJobEvent(BaseModel):
    object: Literal["fine_tuning.job.event"] = Field(
        "fine_tuning.job.event",
        description="The object type, always 'fine_tuning.job.event'.",
    )
    id: str = Field(..., description="The ID of the fine-tuning job event.")
    created_at: int = Field(
        ...,
        description="The Unix timestamp (in seconds) of when the event was created.",
    )
    level: str = Field(..., description="The level of the event (e.g., 'warn').")
    message: str = Field(..., description="The message associated with the event.")
    data: Optional[dict] = Field(
        None, description="Additional data associated with the event, if any."
    )
    type: str = Field(..., description="The type of the event (e.g., 'message').")


class ListFineTuningJobsResponse(BaseModel):
    object: Literal["list"] = Field(
        "list",
        description="The object type, always 'list' for a list of fine-tuning jobs.",
    )
    data: List[FineTuningJobEvent] = Field(
        ..., description="A list of fine-tuning job events."
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
                        "id": "ft-event-TjX0lMfOniCZX64t9PUQT5hn",
                        "created_at": 1689813489,
                        "level": "warn",
                        "message": "Fine tuning process stopping due to job cancellation",
                        "data": None,
                        "type": "message",
                    }
                ],
                "has_more": True,
            }
        }
    )

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class FineTuningJobEvent(BaseModel):
    object: Literal["fine_tuning.job.event"] = Field(
        "fine_tuning.job.event",
        description="The object type, always 'fine_tuning.job.event'.",
    )
    id: str = Field(
        ..., description="The unique identifier for the fine-tuning job event."
    )
    created_at: int = Field(
        ..., description="The Unix timestamp (in seconds) when the event was created."
    )
    level: str = Field(
        ..., description="The level of the event (e.g., 'info', 'warning', 'error')."
    )
    message: str = Field(..., description="The message describing the event.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "object": "fine_tuning.job.event",
                "id": "ftevent-abc123",
                "created_at": 1677610602,
                "level": "info",
                "message": "Created fine-tuning job",
            }
        }
    )

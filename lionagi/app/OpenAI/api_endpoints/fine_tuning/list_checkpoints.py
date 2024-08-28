from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# Request model
class ListFineTuningCheckpointsRequest(BaseModel):
    fine_tuning_job_id: str = Field(
        ..., description="The ID of the fine-tuning job to get checkpoints for."
    )
    after: Optional[str] = Field(
        None,
        description="Identifier for the last checkpoint ID from the previous pagination request.",
    )
    limit: Optional[int] = Field(
        10, description="Number of checkpoints to retrieve.", ge=1
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "fine_tuning_job_id": "ftjob-abc123",
                "after": "ftckpt-123456",
                "limit": 5,
            }
        }
    )


# Response models
class CheckpointMetrics(BaseModel):
    full_valid_loss: float = Field(
        ..., description="The full validation loss for the checkpoint."
    )
    full_valid_mean_token_accuracy: float = Field(
        ..., description="The full validation mean token accuracy for the checkpoint."
    )


class FineTuningCheckpoint(BaseModel):
    object: Literal["fine_tuning.job.checkpoint"] = Field(
        "fine_tuning.job.checkpoint",
        description="The object type, always 'fine_tuning.job.checkpoint'.",
    )
    id: str = Field(..., description="The ID of the checkpoint.")
    created_at: int = Field(
        ...,
        description="The Unix timestamp (in seconds) of when the checkpoint was created.",
    )
    fine_tuned_model_checkpoint: str = Field(
        ..., description="The name of the fine-tuned model checkpoint."
    )
    metrics: CheckpointMetrics = Field(
        ..., description="Metrics associated with the checkpoint."
    )
    fine_tuning_job_id: str = Field(
        ..., description="The ID of the fine-tuning job this checkpoint belongs to."
    )
    step_number: int = Field(
        ...,
        description="The step number of this checkpoint in the fine-tuning process.",
    )


class ListFineTuningCheckpointsResponse(BaseModel):
    object: Literal["list"] = Field(
        "list",
        description="The object type, always 'list' for a list of fine-tuning checkpoints.",
    )
    data: List[FineTuningCheckpoint] = Field(
        ..., description="A list of fine-tuning checkpoints."
    )
    first_id: str = Field(
        ..., description="The ID of the first checkpoint in the list."
    )
    last_id: str = Field(..., description="The ID of the last checkpoint in the list.")
    has_more: bool = Field(
        ..., description="Whether there are more results available after this batch."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "object": "list",
                "data": [
                    {
                        "object": "fine_tuning.job.checkpoint",
                        "id": "ftckpt_zc4Q7MP6XxulcVzj4MZdwsAB",
                        "created_at": 1721764867,
                        "fine_tuned_model_checkpoint": "ft:gpt-4o-mini-2024-07-18:my-org:custom-suffix:96olL566:ckpt-step-2000",
                        "metrics": {
                            "full_valid_loss": 0.134,
                            "full_valid_mean_token_accuracy": 0.874,
                        },
                        "fine_tuning_job_id": "ftjob-abc123",
                        "step_number": 2000,
                    },
                    {
                        "object": "fine_tuning.job.checkpoint",
                        "id": "ftckpt_enQCFmOTGj3syEpYVhBRLTSy",
                        "created_at": 1721764800,
                        "fine_tuned_model_checkpoint": "ft:gpt-4o-mini-2024-07-18:my-org:custom-suffix:7q8mpxmy:ckpt-step-1000",
                        "metrics": {
                            "full_valid_loss": 0.167,
                            "full_valid_mean_token_accuracy": 0.781,
                        },
                        "fine_tuning_job_id": "ftjob-abc123",
                        "step_number": 1000,
                    },
                ],
                "first_id": "ftckpt_zc4Q7MP6XxulcVzj4MZdwsAB",
                "last_id": "ftckpt_enQCFmOTGj3syEpYVhBRLTSy",
                "has_more": True,
            }
        }
    )

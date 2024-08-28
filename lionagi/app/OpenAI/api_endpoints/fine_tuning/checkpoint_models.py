from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class CheckpointMetrics(BaseModel):
    step: float = Field(
        ..., description="The step number associated with these metrics."
    )
    train_loss: float = Field(..., description="The training loss at this step.")
    train_mean_token_accuracy: float = Field(
        ..., description="The mean token accuracy during training at this step."
    )
    valid_loss: float = Field(..., description="The validation loss at this step.")
    valid_mean_token_accuracy: float = Field(
        ..., description="The mean token accuracy during validation at this step."
    )
    full_valid_loss: float = Field(
        ..., description="The full validation loss at this step."
    )
    full_valid_mean_token_accuracy: float = Field(
        ..., description="The full mean token accuracy during validation at this step."
    )


class FineTuningJobCheckpoint(BaseModel):
    object: Literal["fine_tuning.job.checkpoint"] = Field(
        "fine_tuning.job.checkpoint",
        description="The object type, always 'fine_tuning.job.checkpoint'.",
    )
    id: str = Field(
        ..., description="The checkpoint identifier, referenceable in API endpoints."
    )
    created_at: int = Field(
        ..., description="The Unix timestamp (in seconds) of checkpoint creation."
    )
    fine_tuned_model_checkpoint: str = Field(
        ..., description="The name of the fine-tuned checkpoint model created."
    )
    step_number: int = Field(
        ..., description="The step number at which the checkpoint was created."
    )
    metrics: CheckpointMetrics = Field(
        ..., description="Metrics at the step number during the fine-tuning job."
    )
    fine_tuning_job_id: str = Field(
        ..., description="The ID of the fine-tuning job that created this checkpoint."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "object": "fine_tuning.job.checkpoint",
                "id": "ftjob-checkpoint-abc123",
                "created_at": 1677610602,
                "fine_tuned_model_checkpoint": "ft:gpt-3.5-turbo:org-123:custom_suffix:7q8mpxmy",
                "step_number": 100,
                "metrics": {
                    "step": 100,
                    "train_loss": 1.234,
                    "train_mean_token_accuracy": 0.789,
                    "valid_loss": 1.345,
                    "valid_mean_token_accuracy": 0.765,
                    "full_valid_loss": 1.456,
                    "full_valid_mean_token_accuracy": 0.743,
                },
                "fine_tuning_job_id": "ftjob-abc123",
            }
        }
    )

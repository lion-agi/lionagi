from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field, ConfigDict


# Request model
class CancelFineTuningRequest(BaseModel):
    fine_tuning_job_id: str = Field(
        ..., description="The ID of the fine-tuning job to cancel."
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"fine_tuning_job_id": "ftjob-abc123"}}
    )


# Response models
class Hyperparameters(BaseModel):
    n_epochs: Union[Literal["auto"], int] = Field(
        ..., description="Number of epochs for training. Can be 'auto' or an integer."
    )


class CancelledFineTuningJob(BaseModel):
    object: Literal["fine_tuning.job"] = Field(
        "fine_tuning.job", description="The object type, always 'fine_tuning.job'."
    )
    id: str = Field(..., description="The ID of the fine-tuning job.")
    model: str = Field(..., description="The base model used for fine-tuning.")
    created_at: int = Field(
        ..., description="The Unix timestamp (in seconds) of when the job was created."
    )
    fine_tuned_model: Optional[str] = Field(
        None, description="The name of the fine-tuned model, if available."
    )
    organization_id: str = Field(
        ..., description="The ID of the organization that owns the fine-tuning job."
    )
    result_files: List[str] = Field(
        ...,
        description="A list of file IDs for the result files of the fine-tuning job.",
    )
    hyperparameters: Hyperparameters = Field(
        ..., description="The hyperparameters used for the fine-tuning job."
    )
    status: Literal["cancelled"] = Field(
        "cancelled",
        description="The status of the fine-tuning job, which should be 'cancelled'.",
    )
    validation_file: Optional[str] = Field(
        None, description="The file ID of the validation file, if provided."
    )
    training_file: str = Field(..., description="The file ID of the training file.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "object": "fine_tuning.job",
                "id": "ftjob-abc123",
                "model": "gpt-4o-mini-2024-07-18",
                "created_at": 1721764800,
                "fine_tuned_model": None,
                "organization_id": "org-123",
                "result_files": [],
                "hyperparameters": {"n_epochs": "auto"},
                "status": "cancelled",
                "validation_file": "file-abc123",
                "training_file": "file-abc123",
            }
        }
    )

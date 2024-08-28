from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class Hyperparameters(BaseModel):
    n_epochs: int = Field(..., description="Number of epochs for training.")
    batch_size: int = Field(..., description="Batch size for training.")
    learning_rate_multiplier: float = Field(
        ..., description="Learning rate multiplier for training."
    )


class FineTuningJob(BaseModel):
    object: Literal["fine_tuning.job"] = Field(
        "fine_tuning.job", description="The object type, always 'fine_tuning.job'."
    )
    id: str = Field(..., description="The ID of the fine-tuning job.")
    model: str = Field(..., description="The base model used for fine-tuning.")
    created_at: int = Field(
        ..., description="The Unix timestamp (in seconds) of when the job was created."
    )
    finished_at: Optional[int] = Field(
        None,
        description="The Unix timestamp (in seconds) of when the job finished, if applicable.",
    )
    fine_tuned_model: Optional[str] = Field(
        None,
        description="The name of the fine-tuned model, if the job has completed successfully.",
    )
    organization_id: str = Field(
        ..., description="The ID of the organization that owns the fine-tuning job."
    )
    result_files: List[str] = Field(
        ...,
        description="A list of file IDs for the result files of the fine-tuning job.",
    )
    status: str = Field(..., description="The current status of the fine-tuning job.")
    validation_file: Optional[str] = Field(
        None, description="The file ID of the validation file, if provided."
    )
    training_file: str = Field(..., description="The file ID of the training file.")
    hyperparameters: Hyperparameters = Field(
        ..., description="The hyperparameters used for the fine-tuning job."
    )
    trained_tokens: int = Field(
        ..., description="The number of tokens trained on by this job."
    )
    integrations: List[dict] = Field(
        ..., description="A list of integrations used for this fine-tuning job."
    )
    seed: Optional[int] = Field(
        None, description="The seed used for reproducible fine-tuning."
    )
    estimated_finish: Optional[int] = Field(
        None, description="The estimated finish time for the job, if available."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "object": "fine_tuning.job",
                "id": "ftjob-abc123",
                "model": "davinci-002",
                "created_at": 1692661014,
                "finished_at": 1692661190,
                "fine_tuned_model": "ft:davinci-002:my-org:custom_suffix:7q8mpxmy",
                "organization_id": "org-123",
                "result_files": ["file-abc123"],
                "status": "succeeded",
                "validation_file": None,
                "training_file": "file-abc123",
                "hyperparameters": {
                    "n_epochs": 4,
                    "batch_size": 1,
                    "learning_rate_multiplier": 1.0,
                },
                "trained_tokens": 5768,
                "integrations": [],
                "seed": 0,
                "estimated_finish": 0,
            }
        }
    )

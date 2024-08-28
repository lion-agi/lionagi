from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict


class ErrorObject(BaseModel):
    code: str = Field(..., description="A machine-readable error code.")
    message: str = Field(..., description="A human-readable error message.")
    param: Optional[str] = Field(
        None, description="The parameter that was invalid, if applicable."
    )


class Hyperparameters(BaseModel):
    n_epochs: Union[Literal["auto"], int] = Field(
        ...,
        description=("The number of epochs to train the model for. 'auto' or 1-50."),
    )
    batch_size: Optional[int] = Field(None, description="The batch size.")
    learning_rate_multiplier: Optional[float] = Field(
        None, description="The learning rate multiplier."
    )


class WandbIntegration(BaseModel):
    project: str = Field(..., description="The name of the project for the new run.")
    name: Optional[str] = Field(None, description="A display name for the run.")
    entity: Optional[str] = Field(None, description="The entity to use for the run.")
    tags: List[str] = Field(
        default_factory=list, description="A list of tags for the run."
    )


class Integration(BaseModel):
    type: str = Field(..., description="The type of the integration being enabled.")
    wandb: Optional[WandbIntegration] = Field(
        None, description="Settings for Weights and Biases integration."
    )


class FineTuningJob(BaseModel):
    object: Literal["fine_tuning.job"] = Field(
        "fine_tuning.job", description="The object type, always 'fine_tuning.job'."
    )
    id: str = Field(
        ..., description="The object identifier, referenceable in API endpoints."
    )
    created_at: int = Field(
        ..., description="The Unix timestamp (in seconds) of job creation."
    )
    error: Optional[ErrorObject] = Field(
        None, description="Error information for failed jobs."
    )
    fine_tuned_model: Optional[str] = Field(
        None, description="The name of the fine-tuned model being created."
    )
    finished_at: Optional[int] = Field(
        None, description="The Unix timestamp (in seconds) of job completion."
    )
    hyperparameters: Hyperparameters = Field(
        ..., description="The hyperparameters used for the fine-tuning job."
    )
    model: str = Field(..., description="The base model being fine-tuned.")
    organization_id: str = Field(
        ..., description="The organization that owns the fine-tuning job."
    )
    result_files: List[str] = Field(
        ..., description="The compiled results file ID(s) for the job."
    )
    status: str = Field(
        ...,
        description=(
            "The current status of the fine-tuning job: validating_files, "
            "queued, running, succeeded, failed, or cancelled."
        ),
    )
    trained_tokens: Optional[int] = Field(
        None, description="The total number of billable tokens processed."
    )
    training_file: str = Field(..., description="The file ID used for training.")
    validation_file: Optional[str] = Field(
        None, description="The file ID used for validation."
    )
    integrations: Optional[List[Integration]] = Field(
        None, description="A list of integrations enabled for this job."
    )
    seed: Optional[int] = Field(
        None, description="The seed used for the fine-tuning job."
    )
    estimated_finish: Optional[int] = Field(
        None,
        description=("The Unix timestamp (in seconds) for estimated job completion."),
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

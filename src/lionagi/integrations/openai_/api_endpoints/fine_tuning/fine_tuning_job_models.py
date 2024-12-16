from enum import Enum
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from ..data_models import OpenAIEndpointResponseBody


class Status(str, Enum):
    VALIDATING_FILES = "validating_files"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Error(BaseModel):
    code: str | None = Field(
        None, description="A machine-readable error code."
    )

    message: str | None = Field(
        None, description="A human-readable error message."
    )

    param: str | None = Field(
        None, description="The parameter that was invalid, if applicable."
    )


class Hyperparameters(BaseModel):
    n_epochs: Literal["auto"] | int = Field(
        description="The number of epochs to train the model for. 'auto' or 1-50.",
    )

    # TODO: check hyperparameters
    batch_size: Literal["auto"] | int = Field(
        None, description="The batch size."
    )

    learning_rate_multiplier: Literal["auto"] | int = Field(
        None, description="The learning rate multiplier."
    )

    model_config = ConfigDict(extra="allow")


class Wandb(BaseModel):
    project: str = Field(
        ..., description="The name of the project for the new run."
    )

    name: str | None = Field(None, description="A display name for the run.")

    entity: str | None = Field(
        None, description="The entity to use for the run."
    )

    tags: list[str] | None = Field(description="A list of tags for the run.")


class Integration(BaseModel):
    type: str = Field(
        ..., description="The type of the integration being enabled."
    )

    wandb: Wandb | None = Field(
        None, description="Settings for Weights and Biases integration."
    )


class OpenAIFineTuningJobResponseBody(OpenAIEndpointResponseBody):
    id: str = Field(
        description="The object identifier, referenceable in API endpoints."
    )

    created_at: int = Field(
        ..., description="The Unix timestamp (in seconds) of job creation."
    )

    error: Error | None = Field(
        None, description="Error information for failed jobs."
    )

    fine_tuned_model: str | None = Field(
        None, description="The name of the fine-tuned model being created."
    )

    finished_at: int | None = Field(
        None, description="The Unix timestamp (in seconds) of job completion."
    )

    hyperparameters: Hyperparameters = Field(
        description="The hyperparameters used for the fine-tuning job."
    )

    model: str = Field(description="The base model being fine-tuned.")

    object: Literal["fine_tuning.job"] = Field(
        description="The object type, always 'fine_tuning.job'."
    )

    organization_id: str = Field(
        ..., description="The organization that owns the fine-tuning job."
    )

    result_files: list[str] = Field(
        ..., description="The compiled results file ID(s) for the job."
    )

    status: Status = Field(
        description=(
            "The current status of the fine-tuning job: validating_files, "
            "queued, running, succeeded, failed, or cancelled."
        ),
    )

    trained_tokens: int | None = Field(
        None, description="The total number of billable tokens processed."
    )

    training_file: str = Field(description="The file ID used for training.")

    validation_file: str | None = Field(
        None, description="The file ID used for validation."
    )

    integrations: list[Integration] | None = Field(
        None, description="A list of integrations enabled for this job."
    )

    seed: int = Field(
        None, description="The seed used for the fine-tuning job."
    )

    estimated_finish: int | None = Field(
        None,
        description="The Unix timestamp (in seconds) for estimated job completion.",
    )

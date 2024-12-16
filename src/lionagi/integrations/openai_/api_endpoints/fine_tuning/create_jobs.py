from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from ..data_models import OpenAIEndpointRequestBody


class Wandb(BaseModel):
    project: str = Field(
        description="The name of the project for the new run."
    )

    name: str | None = Field(None, description="A display name for the run.")

    entity: str | None = Field(
        None, description="The entity (team or username) for the WandB run."
    )

    tags: list[str] | None = Field(
        None,
        description="A list of tags to be attached to the newly created run.",
    )


class Integration(BaseModel):
    type: Literal["wandb"] = Field(
        description="The type of integration to enable."
        " Only 'wandb' is supported."
    )

    wandb: Wandb = Field(
        description="Settings for Weights and Biases integration."
    )


class Hyperparameters(BaseModel):
    batch_size: str | int | None = Field(
        "auto",
        description=(
            "Number of examples in each batch. A larger"
            " batch size means that "
            "model parameters are updated less frequently, but with lower variance."
        ),
    )
    learning_rate_multiplier: str | float | None = Field(
        "auto",
        description=(
            "Scaling factor for the learning rate. A smaller learning rate "
            "may be useful to avoid overfitting."
        ),
    )
    n_epochs: str | int | None = Field(
        "auto",
        description=(
            "The number of epochs to train the model for. An epoch refers "
            "to one full cycle through the training dataset."
        ),
    )

    # TODO: check hyperparameters
    model_config = ConfigDict(extra="allow")


class OpenAICreateFineTuningJobRequestBody(OpenAIEndpointRequestBody):
    model: str = Field(description="The name of the model to fine-tune.")

    training_file: str = Field(
        description=(
            "The ID of an uploaded file that contains training data. "
            "Must be a JSONL file with 'purpose' set to 'fine-tune'."
        ),
    )

    hyperparameters: Hyperparameters | None = Field(
        None, description="The hyperparameters used for the fine-tuning job."
    )

    suffix: str | None = Field(
        None,
        max_length=64,
        description=(
            "A string of up to 64 characters that will be added to your "
            "fine-tuned model name."
        ),
    )

    validation_file: str | None = Field(
        None,
        description=(
            "The ID of an uploaded file that contains validation data. "
            "Must be a JSONL file with 'purpose' set to 'fine-tune'."
        ),
    )
    integrations: list[Integration] | None = Field(
        None,
        description="A list of integrations to enable for your fine-tuning job.",
    )

    seed: int | None = Field(
        None,
        description=(
            "The seed controls the reproducibility of the job. Passing in the "
            "same seed and job parameters should produce the same results."
        ),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "training_file": "file-BK7bzQj3FfZFXr7DbL6xJwfo",
                "model": "gpt-4o-mini",
                "hyperparameters": {
                    "batch_size": "auto",
                    "learning_rate_multiplier": "auto",
                    "n_epochs": "auto",
                },
                "suffix": "custom-model-name",
                "validation_file": None,
                "integrations": [
                    {
                        "type": "wandb",
                        "wandb": {
                            "project": "my-project",
                            "name": "my-run",
                            "entity": "my-team",
                            "tags": ["tag1", "tag2"],
                        },
                    }
                ],
                "seed": 42,
            }
        }
    )

from typing import Literal

from pydantic import BaseModel, Field

from ..data_models import OpenAIEndpointResponseBody


class Metrics(BaseModel):
    step: int = Field(
        description="The step number associated with these metrics."
    )

    train_loss: float = Field(description="The training loss at this step.")

    train_mean_token_accuracy: float = Field(
        description="The mean token accuracy during training at this step."
    )
    valid_loss: float = Field(description="The validation loss at this step.")

    valid_mean_token_accuracy: float = Field(
        description="The mean token accuracy during validation at this step."
    )

    full_valid_loss: float = Field(
        description="The full validation loss at this step."
    )

    full_valid_mean_token_accuracy: float = Field(
        description="The full mean token accuracy during validation at this step."
    )


class OpenAIFineTuningJobCheckpointResponseBody(OpenAIEndpointResponseBody):
    id: str = Field(description="The ID of the checkpoint.")

    created_at: int = Field(
        description="The Unix timestamp (in seconds) of when the checkpoint was created.",
    )

    fine_tuned_model_checkpoint: str = Field(
        description="The name of the fine-tuned model checkpoint."
    )

    step_number: int = Field(
        description="The step number of this checkpoint in the fine-tuning process.",
    )

    metrics: Metrics = Field(
        description="Metrics associated with the checkpoint."
    )

    fine_tuning_job_id: str = Field(
        description="The ID of the fine-tuning job this checkpoint belongs to."
    )

    object: Literal["fine_tuning.job.checkpoint"] = Field(
        description="The object type, always 'fine_tuning.job.checkpoint'.",
    )

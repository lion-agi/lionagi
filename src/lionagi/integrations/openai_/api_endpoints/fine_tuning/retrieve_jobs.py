from pydantic import Field

from ..data_models import OpenAIEndpointPathParam


class OpenAIRetrieveFineTuningJobPathParam(OpenAIEndpointPathParam):
    fine_tuning_job_id: str = Field(
        description="The ID of the fine-tuning job to get events for."
    )

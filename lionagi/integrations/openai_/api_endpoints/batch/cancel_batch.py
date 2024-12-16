from pydantic import Field

from ..data_models import OpenAIEndpointPathParam


class OpenAICancelBatchPathParam(OpenAIEndpointPathParam):
    batch_id: str = Field(description="The ID of the batch to cancel.")

from pydantic import Field

from ..data_models import OpenAIEndpointPathParam


class OpenAIRetrieveBatchPathParam(OpenAIEndpointPathParam):
    batch_id: str = Field(description="The ID of the batch to retrieve.")

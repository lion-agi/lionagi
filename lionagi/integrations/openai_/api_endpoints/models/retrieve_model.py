from pydantic import Field

from ..data_models import OpenAIEndpointPathParam


class OpenAIRetrieveModelPathParam(OpenAIEndpointPathParam):
    model: str = Field(
        description="The ID of the model to use for this request."
    )

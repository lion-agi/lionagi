from pydantic import Field

from ..data_models import OpenAIEndpointPathParam, OpenAIEndpointResponseBody


class OpenAIDeleteFineTunedModelPathParam(OpenAIEndpointPathParam):
    model: str = Field(description="The model to delete.")


class OpenAIDeleteFineTunedModelResponseBody(OpenAIEndpointResponseBody):
    id: str = Field(
        description="The file identifier, which can be referenced in the API endpoints.",
    )

    object: str = Field(description="The object type, which is always model.")

    deleted: bool = Field(description="The deletion status")

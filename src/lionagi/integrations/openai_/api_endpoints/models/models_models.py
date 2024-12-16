from typing import List, Literal

from pydantic import Field

from ..data_models import OpenAIEndpointResponseBody


class OpenAIModelResponseBody(OpenAIEndpointResponseBody):
    id: str = Field(
        description="The model identifier, which can be referenced in the API endpoints.",
    )

    created: int = Field(
        description="The Unix timestamp (in seconds) when the model was created."
    )

    object: Literal["model"] = Field(
        description="The object type, which is always 'model'."
    )

    owned_by: str = Field(description="The organization that owns the model.")


class OpenAIListModelResponseBody(OpenAIEndpointResponseBody):
    object: Literal["list"] = Field(
        description="The object type, which is always 'list'."
    )

    data: list[OpenAIModelResponseBody] = Field(
        description="The list of model objects."
    )

from typing import Optional

from pydantic import Field

from ..data_models import OllamaEndpointRequestBody, OllamaEndpointResponseBody
from .list_model import Detail


class OllamaShowModelRequestBody(OllamaEndpointRequestBody):
    name: str = Field(description="Name of the model to show")

    verbose: bool | None = Field(
        None,
        description="If set to true, returns full data for verbose response fields",
    )


class OllamaShowModelResponseBody(OllamaEndpointResponseBody):
    license: str = Field(None)

    modelfile: str = Field(None)

    parameters: str = Field(None)

    template: str = Field(None)

    details: Detail = Field(None)

    model_info: dict = Field(None)

    projector_info: dict = Field(None)

    modified_at: str = Field(None)

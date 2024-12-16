from pydantic import Field

from ..data_models import OllamaEndpointRequestBody


class OllamaDeleteModelRequestBody(OllamaEndpointRequestBody):
    name: str = Field(description="Name of the model to delete")

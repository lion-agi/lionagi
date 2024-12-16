from pydantic import Field

from ..data_models import OllamaEndpointRequestBody


class OllamaCopyModelRequestBody(OllamaEndpointRequestBody):
    source: str = Field(description="Name of the source existing model")

    destination: str = Field(description="Name of the copy model")

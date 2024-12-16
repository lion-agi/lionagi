from typing import Optional

from pydantic import Field

from ..data_models import OllamaEndpointRequestBody, OllamaEndpointResponseBody


class OllamaPullModelRequestBody(OllamaEndpointRequestBody):
    name: str = Field(description="Name of the model to pull")

    insecure: bool = Field(
        False,
        description="Allow insecure connections to the library. "
        "Only use this if you are pulling from your own library during development.",
    )

    stream: bool = Field(
        True,
        description="If 'false' the response will be returned as a single response object, "
        "rather than a stream of objects",
    )


class OllamaPullModelResponseBody(OllamaEndpointResponseBody):
    status: str = Field(None)

    digest: str = Field(None)

    total: int = Field(None)

    completed: int = Field(None)

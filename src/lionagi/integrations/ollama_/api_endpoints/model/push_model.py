from typing import Any

from pydantic import Field

from ..data_models import OllamaEndpointRequestBody, OllamaEndpointResponseBody


class OllamaPushModelRequestBody(OllamaEndpointRequestBody):
    name: str = Field(
        description="Name of the model to push in the form of '<namespace>/<model>:<tag>'"
    )

    insecure: Any = Field(
        None,
        description="Allow insecure connections to the library. "
        "Only use this if you are pushing to your library during development.",
    )

    stream: bool = Field(
        True,
        description="If 'false' the response will be returned as a single response object, "
        "rather than a stream of objects",
    )


class OllamaPushModelResponseBody(OllamaEndpointResponseBody):
    status: str = Field(None)

    digest: str = Field(None)

    total: int = Field(None)

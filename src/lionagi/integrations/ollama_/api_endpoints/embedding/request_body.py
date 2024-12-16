from typing import List, Optional

from pydantic import Field

from ..data_models import OllamaEndpointRequestBody
from ..option_models import Option


class OllamaEmbeddingRequestBody(OllamaEndpointRequestBody):
    model: str = Field(description="Name of model to generate embeddings from")

    input: str | list[str] = Field(
        description="Text or list of text to generate embeddings for"
    )

    truncate: bool = Field(
        True,
        description="Truncates the end of each input to fit within context length. "
        "Returns error if 'false' and context length is exceeded.",
    )

    options: Option | None = Field(
        None,
        description="Additional model parameters listed in the documentation for the Modelfile",
    )

    keep_alive: str = Field(
        "5m",
        description="Controls how long the model will stay loaded into memory following the request.",
    )

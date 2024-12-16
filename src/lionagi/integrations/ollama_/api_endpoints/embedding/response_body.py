from pydantic import Field

from ..data_models import OllamaEndpointResponseBody


class OllamaEmbeddingResponseBody(OllamaEndpointResponseBody):
    model: str = Field(None, description="The model name")

    embeddings: list = Field(
        None,
        description="The generated embeddings for the text or list of text",
    )

    total_duration: int = Field(
        None, description="Time spent generating the response"
    )

    load_duration: int = Field(
        None, description="Time spent in nanoseconds loading the model"
    )

    prompt_eval_count: int = Field(
        None, description="Number of tokens in the prompt"
    )

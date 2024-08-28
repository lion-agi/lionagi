from typing import List, Literal
from pydantic import BaseModel, Field, ConfigDict


class EmbeddingObject(BaseModel):
    index: int = Field(
        ..., description="The index of the embedding in the list of embeddings."
    )
    embedding: List[float] = Field(
        ...,
        description=(
            "The embedding vector, which is a list of floats. The length of "
            "vector depends on the model as listed in the embedding guide."
        ),
    )
    object: Literal["embedding"] = Field(
        "embedding", description='The object type, which is always "embedding".'
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "index": 0,
                "embedding": [0.0023064255, -0.009327292, ..., -0.0028842222],
                "object": "embedding",
            }
        }
    )


class EmbeddingUsage(BaseModel):
    prompt_tokens: int = Field(..., description="The number of tokens in the prompt.")
    total_tokens: int = Field(
        ..., description="The total number of tokens used in the request."
    )


class OpenAIEmbeddingResponse(BaseModel):
    object: Literal["list"] = Field(
        "list", description='The object type, which is always "list" for embeddings.'
    )
    data: List[EmbeddingObject] = Field(
        ..., description="The list of embedding objects."
    )
    model: str = Field(
        ..., description="The ID of the model used to generate the embeddings."
    )
    usage: EmbeddingUsage = Field(
        ..., description="The usage statistics for the request."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "object": "list",
                "data": [
                    {
                        "index": 0,
                        "embedding": [0.0023064255, -0.009327292, ..., -0.0028842222],
                        "object": "embedding",
                    }
                ],
                "model": "text-embedding-ada-002",
                "usage": {"prompt_tokens": 8, "total_tokens": 8},
            }
        }
    )

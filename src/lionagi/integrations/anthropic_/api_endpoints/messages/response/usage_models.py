from pydantic import BaseModel, Field


class Usage(BaseModel):
    input_tokens: int = Field(
        description="The number of input tokens which were used"
    )

    output_tokens: int = Field(
        description="The number of output tokens which were used"
    )

    cache_creation_input_tokens: int | None = Field(
        default=None,
        description="The number of input tokens used to create the cache entry",
    )

    cache_read_input_tokens: int | None = Field(
        default=None,
        description="The number of input tokens read from the cache",
    )

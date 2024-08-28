from pydantic import BaseModel, Field


class Usage(BaseModel):
    prompt_tokens: int = Field(description="Number of tokens in the prompt.")
    completion_tokens: int = Field(
        description="Number of tokens in the generated completion."
    )
    total_tokens: int = Field(
        description="Total number of tokens used in the request (prompt + completion)"
    )

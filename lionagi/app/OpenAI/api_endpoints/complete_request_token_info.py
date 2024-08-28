from pydantic import BaseModel, Field


class CompleteRequestTokenInfo(BaseModel):
    timestamp: float = Field(description="HTTP response generated time")
    token_usage: int = Field(description="Number of tokens used in the request")

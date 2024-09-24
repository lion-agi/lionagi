from pydantic import BaseModel, Field


class CompleteRequestInfo(BaseModel):
    timestamp: float = Field(description="HTTP response generated time")


class CompleteRequestTokenInfo(CompleteRequestInfo):
    token_usage: int = Field(description="Number of tokens used in the request")

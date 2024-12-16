from typing import List, Optional

from pydantic import BaseModel, Field


class TokenLogProb(BaseModel):
    token: str = Field(description="The token.")
    logprob: float = Field(
        description=(
            "The log probability of this token, if it is within the top 20 "
            "most likely tokens. Otherwise, the value -9999.0 is used to "
            "signify that the token is very unlikely."
        )
    )
    bytes: list[int] | None = Field(
        None,
        description=(
            "A list of integers representing the UTF-8 bytes representation "
            "of the token. Useful in instances where characters are "
            "represented by multiple tokens and their byte representations "
            "must be combined to generate the correct text representation. "
            "Can be null if there is no bytes representation for the token."
        ),
    )


class LogProbContent(TokenLogProb):
    top_logprobs: list[TokenLogProb] = Field(
        description=(
            "List of the most likely tokens and their log probability, at "
            "this token position. In rare cases, there may be fewer than the "
            "number of requested top_logprobs returned."
        )
    )


class LogProbs(BaseModel):
    content: list[LogProbContent] | None = Field(
        None,
        description="A list of message content "
        "tokens with log probability information.",
    )
    refusal: list[LogProbContent] | None = Field(
        None,
        description="A list of message refusal "
        "tokens with log probability information.",
    )

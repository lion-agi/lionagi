from typing import Optional
from pydantic import BaseModel, Field
from .types import FinishReasonLiteral
from .message_models import Message
from .log_prob_models import LogProbs


class Choice(BaseModel):
    index: int = Field(description="The index of the choice in the list of choices.")
    message: Message = Field(
        description="A chat completion message generated by the model."
    )
    logprobs: Optional[LogProbs] = Field(
        None, description="Log probability information for the choice."
    )
    finish_reason: FinishReasonLiteral = Field(
        description=(
            "The reason the model stopped generating tokens. This will be "
            "stop if the model hit a natural stop point or a provided stop "
            "sequence, length if the maximum number of tokens specified in "
            "the request was reached, content_filter if content was omitted "
            "due to a flag from our content filters, tool_calls if the model "
            "called a tool, or function_call (deprecated) if the model "
            "called a function."
        )
    )
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from .choice_models import Choice
from .usage_models import Usage


class OpenAIChatCompletionResponseBody(BaseModel):
    id: str = Field(description="A unique identifier for the chat completion.")
    object: Literal["chat.completion"] = Field(
        description="The object type, which is always chat.completion."
    )
    created: int = Field(
        description=(
            "The Unix timestamp (in seconds) of when the chat completion "
            "was created."
        )
    )
    model: str = Field(description="The model used for the chat completion.")
    system_fingerprint: str = Field(
        description=(
            "This fingerprint represents the backend configuration that the "
            "model runs with. Can be used in conjunction with the seed "
            "request parameter to understand when backend changes have been "
            "made that might impact determinism."
        )
    )
    choices: List[Choice] = Field(
        description=(
            "A list of chat completion choices. Can be more than one if n "
            "is greater than 1."
        )
    )
    usage: Usage = Field(description="Usage statistics for the completion request.")
    service_tier: Optional[str] = Field(
        None,
        description=(
            "The service tier used for processing the request. This field is "
            "only included if the service_tier parameter is specified in the "
            "request."
        ),
    )

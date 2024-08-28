# File: chat_completion_request.py
from typing import Dict, List
from pydantic import BaseModel, Field, model_validator
from .types import ServiceTierLiteral, ToolChoiceLiteral
from .message_models import Message
from .function_models import Tool, ToolChoice
from .response_format import ResponseFormat
from .stream_options import StreamOptions


class OpenAIChatCompletionRequest(BaseModel):
    model: str = Field(description="ID of the model to use.")
    messages: List[Message] = Field(
        description="A list of messages comprising the conversation so far."
    )
    temperature: float | None = Field(
        1.0,
        ge=0,
        le=2,
        description=(
            "What sampling temperature to use, between 0 and 2. Higher values "
            "like 0.8 will make the output more random, while lower values "
            "like 0.2 will make it more focused and deterministic."
        ),
    )
    top_p: float | None = Field(
        1.0,
        ge=0,
        le=1,
        description=(
            "An alternative to sampling with temperature, called nucleus "
            "sampling, where the model considers the results of the tokens "
            "with top_p probability mass. So 0.1 means only the tokens "
            "comprising the top 10% probability mass are considered."
        ),
    )
    n: int | None = Field(
        1,
        ge=1,
        description=(
            "How many chat completion choices to generate for each input "
            "message. Note that you will be charged based on the number of "
            "generated tokens across all of the choices. Keep n as 1 to "
            "minimize costs."
        ),
    )
    stream: bool | None = Field(
        False,
        description=(
            "If set, partial message deltas will be sent, like in ChatGPT. "
            "Tokens will be sent as data-only server-sent events as they "
            "become available, with the stream terminated by a data: [DONE] "
            "message."
        ),
    )
    stop: str | List[str] | None = Field(
        None,
        max_items=4,
        description=(
            "Up to 4 sequences where the API will stop generating further " "tokens."
        ),
    )
    max_tokens: int | None = Field(
        None,
        description=(
            "The maximum number of tokens that can be generated in the chat "
            "completion. The total length of input tokens and generated "
            "tokens is limited by the model's context length."
        ),
    )
    presence_penalty: float | None = Field(
        0,
        ge=-2.0,
        le=2.0,
        description=(
            "Number between -2.0 and 2.0. Positive values penalize new tokens "
            "based on whether they appear in the text so far, increasing the "
            "model's likelihood to talk about new topics."
        ),
    )
    frequency_penalty: float | None = Field(
        0,
        ge=-2.0,
        le=2.0,
        description=(
            "Number between -2.0 and 2.0. Positive values penalize new tokens "
            "based on their existing frequency in the text so far, decreasing "
            "the model's likelihood to repeat the same line verbatim."
        ),
    )
    logit_bias: Dict[str, float] | None = Field(
        None,
        description=(
            "Modify the likelihood of specified tokens appearing in the "
            "completion. Accepts a JSON object that maps tokens (specified by "
            "their token ID in the tokenizer) to an associated bias value from "
            "-100 to 100."
        ),
    )
    user: str | None = Field(
        None,
        description=(
            "A unique identifier representing your end-user, which can help "
            "OpenAI to monitor and detect abuse."
        ),
    )
    response_format: ResponseFormat | None = Field(
        None,
        description=(
            "An object specifying the format that the model must output. "
            "Compatible with GPT-4o, GPT-4o mini, GPT-4 Turbo and all GPT-3.5 "
            "Turbo models newer than gpt-3.5-turbo-1106. Setting to "
            "{ 'type': 'json_schema', 'json_schema': {...} } enables "
            "Structured Outputs. Setting to { 'type': 'json_object' } enables "
            "JSON mode. Important: when using JSON mode, you must also "
            "instruct the model to produce JSON via a system or user message."
        ),
    )
    seed: int | None = Field(
        None,
        description=(
            "This feature is in Beta. If specified, our system will make a "
            "best effort to sample deterministically, such that repeated "
            "requests with the same seed and parameters should return the "
            "same result."
        ),
    )
    tools: List[Tool] | None = Field(
        None,
        max_items=128,
        description=(
            "A list of tools the model may call. Currently, only functions "
            "are supported as a tool. Use this to provide a list of functions "
            "the model may generate JSON inputs for."
        ),
    )
    tool_choice: ToolChoiceLiteral | ToolChoice | None = Field(
        "auto",
        description=(
            "Controls which (if any) tool is called by the model. 'none' "
            "means the model will not call a tool and instead generates a "
            "message. 'auto' means the model can pick between generating a "
            "message or calling a tool. 'required' means the model must call "
            "a tool."
        ),
    )
    logprobs: bool | None = Field(
        False,
        description=(
            "Whether to return log probabilities of the output tokens or not. "
            "If true, returns the log probabilities of each output token "
            "returned in the content of message."
        ),
    )
    top_logprobs: int | None = Field(
        None,
        ge=0,
        le=20,
        description=(
            "An integer between 0 and 20 specifying the number of most likely "
            "tokens to return at each token position, each with an associated "
            "log probability. logprobs must be true if this parameter "
            "is used."
        ),
    )
    service_tier: ServiceTierLiteral | None = Field(
        None,
        description=(
            "Specifies the latency tier to use for processing the request. "
            "This parameter is relevant for customers subscribed to the scale "
            "tier service."
        ),
    )
    stream_options: StreamOptions | None = Field(
        None,
        description=(
            "Options for streaming response. Only set this when you set "
            "stream: true."
        ),
    )

    @model_validator(mode="after")
    def validate_request(self) -> "OpenAIChatCompletionRequest":
        if self.tools is None and self.tool_choice not in [None, "none", "auto"]:
            raise ValueError(
                "tool_choice must be 'none' or 'auto' when tools is not provided"
            )
        if self.tools and self.tool_choice == "none":
            raise ValueError("tool_choice cannot be 'none' when tools are provided")
        if self.top_logprobs is not None and not self.logprobs:
            raise ValueError("logprobs must be true when top_logprobs is set")
        return self

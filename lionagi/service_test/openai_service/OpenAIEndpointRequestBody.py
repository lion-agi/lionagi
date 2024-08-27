from pydantic import BaseModel, Field


class OpenAIEndpointRequestBody(BaseModel):
    pass


class OpenAIChatCompletionsRequestBody(OpenAIEndpointRequestBody):
    messages: list = Field(
        description="A list of messages comprising the conversation so far."
    )

    model: str = Field(description="ID of the model to use.")

    frequency_penalty: float | None = Field(
        default=0,
        description="Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing "
        "frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.",
    )

    logit_bias: dict | None = Field(
        default=None,
        description="Modify the likelihood of specified tokens appearing in the completion.",
    )

    logprobs: bool | None = Field(
        default=False,
        description="Whether to return log probabilities of the output tokens or not. If true, returns the log "
        "probabilities of each output token returned in the content of message.",
    )

    top_logprobs: int | None = Field(
        default=None,
        description="An integer between 0 and 20 specifying the number of most likely tokens to return at each token "
        "position, each with an associated log probability. logprobs must be set to true if this parameter "
        "is used.",
    )

    max_tokens: int | None = Field(
        default=None,
        description="The maximum number of tokens that can be generated in the chat completion.",
    )

    n: int | None = Field(
        default=1,
        description="How many chat completion choices to generate for each input message. Note that you will be "
        "charged based on the number of generated tokens across all of the choices. Keep n as 1 to "
        "minimize costs.",
    )

    presence_penalty: float | None = Field(
        default=0,
        description="Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in "
        "the text so far, increasing the model's likelihood to talk about new topics.",
    )

    response_format: dict | None = Field(
        default=None,
        description="An object specifying the format that the model must output. Compatible with GPT-4o, GPT-4o mini, "
        "GPT-4 Turbo and all GPT-3.5 Turbo models newer than gpt-3.5-turbo-1106.",
    )

    seed: int | None = Field(default=None, description="This feature is in Beta.")

    service_tier: str | None = Field(
        default=None,
        description="Specifies the latency tier to use for processing the request.",
    )

    stop: str | list | None = Field(
        default=None,
        description="Up to 4 sequences where the API will stop generating further tokens.",
    )

    stream: bool | None = Field(
        default=None,
        description="If set, partial message deltas will be sent, like in ChatGPT.",
    )

    stream_options: dict | None = Field(
        default=None,
        description="Options for streaming response. Only set this when you set stream: true.",
    )

    temperature: float | None = Field(
        default=1,
        description="What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output "
        "more random, while lower values like 0.2 will make it more focused and deterministic.",
    )

    top_p: float | None = Field(
        default=1,
        description="An alternative to sampling with temperature, called nucleus sampling, where the model considers "
        "the results of the tokens with top_p probability mass。",
    )

    tools: list | None = Field(
        default=None, description="A list of tools the model may call."
    )

    tool_choice: str | dict | None = Field(
        default=None, description="Controls which (if any) tool is called by the model."
    )

    parallel_tool_calls: bool = Field(
        default=True,
        description="Whether to enable parallel function calling during tool use.",
    )

    user: str | None = Field(
        default=None,
        description="A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse.",
    )

from pydantic import BaseModel, Field
from enum import Enum
from lionagi.service.endpoints.base import EndpointRequest, EndpointOptions



class OpenAIChatRole(str, Enum):
    developer = "developer"  # For o1 series (replaces system)
    system = "system"        # Older style, still used for many models
    user = "user"
    assistant = "assistant"
    tool = "tool"            # For function/tool responses
    function = "function"    # Deprecated by OpenAI, but can appear


class OpenAIToolFunction(BaseModel):
    """
    The function that the model wants to call.
    Example:
      {
         "name": "get_current_weather",
         "arguments": "{\"location\": \"Paris\", \"format\": \"celsius\"}"
      }
    """
    name: str = Field(
        ...,
        description="The name of the function to call."
    )
    arguments: str = Field(
        ...,
        description="JSON-formatted string of arguments. Must be validated on your side."
    )


class OpenAIToolCall(BaseModel):
    """
    The top-level object describing a single call to a function (tool).
    Example:
      {
        "id": "toolcall-1234",
        "type": "function",
        "function": {
          "name": "get_current_weather",
          "arguments": "{\"location\":\"Paris\", \"format\":\"celsius\"}"
        }
      }
    """
    id: str = Field(..., description="Unique ID of the tool call.")
    type: str = Field(..., description="Type of the tool, currently only 'function'.")
    function: OpenAIToolFunction = Field(
        ...,
        description="The function that was called."
    )


class OpenAIAudioData(BaseModel):
    """
    If the assistant produced an audio response, details about that audio.
    Example:
      {
        "id": "audio-12345"
      }
    """
    id: str = Field(..., description="Unique identifier for a previous audio response.")


class OpenAIChatMessage(BaseModel):
    """
    A single chat message object. 
    `content` can be string or list of strings. 
    Some fields only apply to certain roles.
    """
    role: OpenAIChatRole = Field(..., description="The role of the message author.")
    content: str | list[str] | dict | None = Field(
        default=None,
        description="The main text content of the message. Required except for certain function calls or tool responses."
    )
    name: str | None = Field(
        default=None,
        description="Optional name for the participant, helps differentiate messages of the same role."
    )

    # Fields specifically for assistant role:
    refusal: str | None = Field(
        default=None,
        description="If the assistant refused the request, store the refusal text here."
    )
    audio: OpenAIAudioData | None = Field(
        default=None,
        description="Audio info if the assistant returned an audio response."
    )
    tool_calls: list[OpenAIToolCall] | None = Field(
        default=None,
        description="List of tool calls the assistant made (function calls)."
    )
    
    # Fields specifically for role=tool:
    tool_call_id: str | None = Field(
        default=None,
        description="Tool call ID this message is responding to, if role=tool."
    )
    
    
class OpenAIChatCompletionOptions(EndpointOptions):
    
    # Basic optional fields
    store: bool | None = Field(
        default=False,
        description="Whether to store the output for model distillation or evals. Defaults to false."
    )
    reasoning_effort: str | None = Field(
        default="medium",
        description="(o1 models only) 'low', 'medium', or 'high'."
    )
    metadata: dict | None = Field(
        default=None,
        description="Developer-defined tags/values used for filtering completions in the dashboard."
    )

    # Sampling + penalty parameters
    frequency_penalty: float | None = Field(
        default=0.0,
        description="Penalize new tokens based on frequency in the text so far, -2.0 to 2.0."
    )
    presence_penalty: float | None = Field(
        default=0.0,
        description="Penalize tokens that have appeared so far, -2.0 to 2.0."
    )
    temperature: float | None = Field(
        default=1.0,
        description="Sampling temperature, between 0 and 2. Higher => more randomness."
    )
    top_p: float | None = Field(
        default=1.0,
        description="Nucleus sampling. Only tokens comprising top_p probability mass considered."
    )

    # Logprobs
    logit_bias: dict[str, float] | None = Field(
        default=None,
        description="Dictionary that modifies likelihood of specified tokens appearing. token_id -> bias."
    )
    logprobs: bool | None = Field(
        default=False,
        description="If True, returns log probabilities of output tokens in the response."
    )
    top_logprobs: int | None = Field(
        default=None,
        description="Number of top tokens with log probabilities to return (0 to 20). logprobs must be True."
    )

    # Max tokens
    max_tokens: int | None = Field(
        default=None,
        description=(
            "Deprecated in favor of max_completion_tokens. Maximum tokens to generate. "
            "Not compatible with o1 series models."
        )
    )
    max_completion_tokens: int | None = Field(
        default=None,
        description="Upper bound for total tokens the model may generate (including reasoning)."
    )

    # Number of outputs
    n: int | None = Field(
        default=1,
        description="How many chat completion choices to generate for each prompt."
    )

    # Output modalities
    modalities: list[str] | None = Field(
        default=None,
        description=(
            "Which output formats to produce, e.g. ['text'] or ['text','audio'] for gpt-4o-audio-preview."
        )
    )

    # Streaming
    stream: bool | None = Field(
        default=False,
        description="If True, partial tokens are streamed as they are generated (SSE)."
    )
    stream_options: dict | None = Field(
        default=None,
        description="Additional streaming options, if needed."
    )

    # Stopping
    stop: str | list[str] | None = Field(
        default=None,
        description="Up to 4 sequences where the API will stop generating further tokens."
    )

    # Tools / Functions
    tools: list[dict] | None = Field(
        default=None,
        description=(
            "List of tool definitions (functions) the model can call. Each item has 'type'='function' "
            "and a 'function' object with name/description/parameters."
        )
    )
    tool_choice: str | dict | None = Field(
        default=None,
        description=(
            "Controls which (if any) tool is called by the model. 'none', 'auto', 'required', "
            "or an object forcing a specific function call."
        )
    )
    parallel_tool_calls: bool | None = Field(
        default=True,
        description="If True, enable parallel function calling. Usually default is True."
    )

    # (Deprecated) function_call, functions
    function_call: str | dict | None = Field(
        default=None,
        description="Deprecated alias for tool_choice. 'none', 'auto', or {'name': 'some_function'}."
    )
    functions: list[dict] | None = Field(
        default=None,
        description="Deprecated alias for 'tools'."
    )

    # Response formatting
    response_format: dict | None = Field(
        default=None,
        description=(
            "An object specifying the format the model must output. E.g. "
            "{ 'type': 'json_schema', 'json_schema': {...} } or { 'type': 'json_object' } "
            "for structured outputs. Must also instruct the model accordingly in your messages."
        )
    )

    # Prediction config
    prediction: dict | None = Field(
        default=None,
        description=(
            "Configuration for Predicted Output to speed up generation if parts of the text are known in advance."
        )
    )

    # Audio output
    # (If you set modalities=['audio'], you can specify details in here.)
    audio: dict | None = Field(
        default=None,
        description=(
            "Audio output configuration if generating audio (e.g., voice='ballad', format='mp3')."
        )
    )

    # Additional
    seed: int | None = Field(
        default=None,
        description=(
            "Beta feature. If specified, attempts to sample deterministically. "
            "No guarantee for full determinism, but best effort."
        )
    )
    service_tier: str | None = Field(
        default="auto",
        description=(
            "Specifies the latency tier. 'auto' uses scale tier credits if available. "
            "'default' uses normal tier with fewer guarantees."
        )
    )
    user: str | None = Field(
        default=None,
        description="Unique identifier representing your end-user (for abuse monitoring)."
    )

    
class OpenAIChatCompletionRequest(EndpointRequest):
    """
    Represents the request body for OpenAI's Chat Completions endpoint.
    Endpoint: POST https://api.openai.com/v1/chat/completions
    """
    model: str = Field(
        ...,
        description="ID of the model to use, e.g. 'gpt-4o', 'gpt-3.5-turbo', etc."
    )
    messages: list[OpenAIChatMessage] = Field(
        ...,
        description="A list of messages forming the conversation so far."
    )
    options: OpenAIChatCompletionOptions = Field(
        ...,
        description="Options for the chat completion request."
    )
from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field


#
# Common / Shared Models
#


class Options(BaseModel):
    """
    Corresponds to the 'options' object (advanced model-specific parameters).
    This includes parameters like 'temperature', 'top_k', 'seed', etc.

    For simplicity, all parameters are typed as optional fields.
    Fill in or remove as needed to reflect your usage or the modelfile docs.
    """

    num_keep: int | None = None
    seed: int | None = None
    num_predict: int | None = None
    top_k: int | None = None
    top_p: float | None = None
    min_p: float | None = None
    typical_p: float | None = None
    repeat_last_n: int | None = None
    temperature: float | None = None
    repeat_penalty: float | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    mirostat: int | None = None
    mirostat_tau: float | None = None
    mirostat_eta: float | None = None
    penalize_newline: bool | None = None
    stop: list[str] | None = None
    numa: bool | None = None
    num_ctx: int | None = None
    num_batch: int | None = None
    num_gpu: int | None = None
    main_gpu: int | None = None
    low_vram: bool | None = None
    vocab_only: bool | None = None
    use_mmap: bool | None = None
    use_mlock: bool | None = None
    num_thread: int | None = None


class StatusResponse(BaseModel):
    """
    Many streaming endpoints return JSON objects with a 'status' string.
    This model can be used to parse those partial / status updates.
    """

    status: str
    digest: str | None = None
    total: int | None = None
    completed: int | None = None


#
# /api/generate
#


class GenerateRequest(BaseModel):
    """
    Request body for:
    POST /api/generate
    """

    model: str
    prompt: str | None = None
    suffix: str | None = None
    images: list[str] | None = None
    format: str | dict[str, Any] | None = None  # 'json' or JSON schema
    options: Options | None = None
    system: str | None = None
    template: str | None = None
    stream: bool | None = None
    raw: bool | None = None
    keep_alive: str | None = None  # e.g. "5m"
    # Deprecated field:
    context: list[int] | None = None


class GenerateResponse(BaseModel):
    """
    Response body for:
    POST /api/generate
    (Handles both streaming chunks and final object in one model,
     with optional fields that appear only in final chunk.)
    """

    model: str
    created_at: datetime
    response: str | None = None  # Full or partial response text
    done: bool
    # The final chunk includes these fields:
    context: list[int] | None = None
    total_duration: int | None = None  # in nanoseconds
    load_duration: int | None = None  # in nanoseconds
    prompt_eval_count: int | None = None
    prompt_eval_duration: int | None = None  # in nanoseconds
    eval_count: int | None = None
    eval_duration: int | None = None  # in nanoseconds
    done_reason: str | None = None


#
# /api/chat
#


class ChatToolFunctionParameters(BaseModel):
    """
    A generic placeholder for tool function parameters, since
    the actual JSON schema can vary.
    """

    type: str
    properties: dict[str, Any]
    required: list[str] | None = None


class ChatToolFunction(BaseModel):
    """
    For 'tools' => 'function' in a chat request.
    """

    name: str
    description: str | None = None
    parameters: ChatToolFunctionParameters | None = None


class ChatToolDefinition(BaseModel):
    """
    Tools array item for chat requests.
    Example: {"type": "function", "function": {...}}
    """

    type: str
    function: ChatToolFunction


class ChatToolFunctionCall(BaseModel):
    """
    The model for a tool usage call in the assistant's message response.
    e.g.:
    {
      "function": {
        "name": "get_current_weather",
        "arguments": {...}
      }
    }
    """

    name: str
    arguments: dict[str, Any]


class ChatToolCall(BaseModel):
    """
    Single item in 'tool_calls':
    {
      "function": {
        "name": "...",
        "arguments": {...}
      }
    }
    """

    function: ChatToolFunctionCall


class ChatMessage(BaseModel):
    """
    Chat message object used in the request 'messages' array.
    """

    role: str  # "system", "user", "assistant", or "tool"
    content: str
    images: list[str] | None = None
    # For the request (tool messages) or for the response (assistant messages using tools):
    tool_calls: list[ChatToolCall] | None = None


class ChatRequest(BaseModel):
    """
    Request body for:
    POST /api/chat
    """

    model: str
    messages: list[ChatMessage]
    # Tools are only valid if 'stream': false, according to docs.
    tools: list[ChatToolDefinition] | None = None
    format: str | dict[str, Any] | None = None
    options: Options | None = None
    stream: bool | None = None
    keep_alive: str | None = None


class ChatMessageResponse(BaseModel):
    """
    Subobject for the 'message' field in chat responses.
    """

    role: str
    content: str
    images: list[str] | None = None
    # If the model calls any tools:
    tool_calls: list[ChatToolCall] | None = None


class ChatResponse(BaseModel):
    """
    Response body for:
    POST /api/chat
    (Covers both streaming and final chunk.)
    """

    model: str
    created_at: datetime
    message: ChatMessageResponse | None = None
    done: bool | None = None
    done_reason: str | None = None
    # Additional data included in the final chunk:
    total_duration: int | None = None
    load_duration: int | None = None
    prompt_eval_count: int | None = None
    prompt_eval_duration: int | None = None
    eval_count: int | None = None
    eval_duration: int | None = None


#
# /api/create
#


class CreateModelRequest(BaseModel):
    """
    Request body for:
    POST /api/create
    """

    model: str
    from_: str | None = Field(None, alias="from")
    files: dict[str, str] | None = None  # mapping: filename -> sha256 digest
    adapters: dict[str, str] | None = None  # LORA adapters
    template: str | None = None
    license: str | list[str] | None = None
    system: str | None = None
    parameters: dict[str, Any] | None = None
    messages: list[ChatMessage] | None = None
    stream: bool | None = None
    quantize: str | None = None


class CreateModelResponse(BaseModel):
    """
    Response body for:
    POST /api/create
    In practice, this is returned as a streaming series of status messages,
    each a JSON object. If the final status is "success", creation is complete.

    This model can represent each streamed chunk if needed (like StatusResponse).
    """

    status: str
    # Optional fields that may appear in intermediate messages:
    digest: str | None = None


#
# /api/tags (List Local Models)
#


class LocalModelDetails(BaseModel):
    format: str | None = None
    family: str | None = None
    families: list[str] | None = None
    parameter_size: str | None = None
    quantization_level: str | None = None


class LocalModelInfo(BaseModel):
    name: str
    modified_at: str
    size: int
    digest: str
    details: LocalModelDetails


class ListLocalModelsResponse(BaseModel):
    models: list[LocalModelInfo]


#
# /api/show (Show Model Information)
#


class ShowModelRequest(BaseModel):
    model: str
    verbose: bool | None = None


class ShowModelDetails(BaseModel):
    parent_model: str | None = None
    format: str | None = None
    family: str | None = None
    families: list[str] | None = None
    parameter_size: str | None = None
    quantization_level: str | None = None


class ShowModelResponse(BaseModel):
    modelfile: str | None = None
    parameters: str | None = None
    template: str | None = None
    details: ShowModelDetails | None = None
    # model_info can be a large dictionary of metadata fields
    model_info: dict[str, Any] | None = None


#
# /api/copy
#


class CopyModelRequest(BaseModel):
    """
    Request body for:
    POST /api/copy
    """

    source: str
    destination: str


#
# /api/delete
#


class DeleteModelRequest(BaseModel):
    """
    Request body for:
    DELETE /api/delete
    """

    model: str


#
# /api/pull
#


class PullModelRequest(BaseModel):
    """
    Request body for:
    POST /api/pull
    """

    model: str
    insecure: bool | None = None
    stream: bool | None = None


class PullModelResponse(BaseModel):
    """
    Similar to Create/Push streaming approach,
    each chunk is typically a JSON with "status" etc.
    Final chunk has "status": "success".
    """

    status: str
    digest: str | None = None
    total: int | None = None
    completed: int | None = None


#
# /api/push
#


class PushModelRequest(BaseModel):
    """
    Request body for:
    POST /api/push
    """

    model: str
    insecure: bool | None = None
    stream: bool | None = None


class PushModelResponse(BaseModel):
    """
    Streaming status messages during the push.
    """

    status: str
    digest: str | None = None
    total: int | None = None
    completed: int | None = None


#
# /api/embed
#


class EmbedRequest(BaseModel):
    """
    Request body for:
    POST /api/embed
    """

    model: str
    input: str | list[str]
    truncate: bool | None = None  # default: true
    options: Options | None = None
    keep_alive: str | None = None


class EmbedResponse(BaseModel):
    """
    Response body for:
    POST /api/embed
    """

    model: str
    embeddings: list[list[float]]
    total_duration: int | None = None  # in nanoseconds
    load_duration: int | None = None  # in nanoseconds
    prompt_eval_count: int | None = None


#
# /api/ps (List Running Models)
#


class RunningModelDetails(BaseModel):
    parent_model: str | None = None
    format: str | None = None
    family: str | None = None
    families: list[str] | None = None
    parameter_size: str | None = None
    quantization_level: str | None = None


class RunningModelInfo(BaseModel):
    name: str
    model: str
    size: int
    digest: str
    details: RunningModelDetails
    expires_at: str | None = None
    size_vram: int | None = None


class ListRunningModelsResponse(BaseModel):
    models: list[RunningModelInfo]


#
# /api/embeddings (Legacy Embeddings Endpoint)
#


class LegacyEmbeddingsRequest(BaseModel):
    """
    Request body for:
    POST /api/embeddings
    Note: superseded by /api/embed
    """

    model: str
    prompt: str
    options: Options | None = None
    keep_alive: str | None = None


class LegacyEmbeddingsResponse(BaseModel):
    """
    Response body for:
    POST /api/embeddings
    """

    embedding: list[float]


#
# /api/version
#


class VersionResponse(BaseModel):
    version: str

from pydantic import BaseModel, Field
from typing import Optional, List, Union, Dict, Any
from enum import Enum


class GenerateOptions(BaseModel):
    """
    Advanced model parameters for controlling generation.
    """
    num_keep: Optional[int] = Field(
        default=None,
        description="Number of tokens from the prompt to keep in the context window."
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducible outputs."
    )
    num_predict: Optional[int] = Field(
        default=None,
        description="Maximum tokens to predict for the response."
    )
    top_k: Optional[int] = Field(
        default=None,
        description="The top_k parameter for sampling, typically 20 or so."
    )
    top_p: Optional[float] = Field(
        default=None,
        description="The top_p parameter for nucleus sampling, e.g. 0.9."
    )
    min_p: Optional[float] = Field(
        default=None,
        description="Minimum probability for nucleus sampling. Rarely used."
    )
    typical_p: Optional[float] = Field(
        default=None,
        description="Typical P sampling—another sampling method."
    )
    repeat_last_n: Optional[int] = Field(
        default=None,
        description="How many tokens to look back at for repetition penalty."
    )
    temperature: Optional[float] = Field(
        default=None,
        description="Temperature for sampling, e.g. 0.7 or 0.8."
    )
    repeat_penalty: Optional[float] = Field(
        default=None,
        description="Controls how strongly to penalize repeated tokens, e.g. 1.2."
    )
    presence_penalty: Optional[float] = Field(
        default=None,
        description="Penalizes new tokens if they've already appeared."
    )
    frequency_penalty: Optional[float] = Field(
        default=None,
        description="Penalizes repeated tokens by frequency in text."
    )
    mirostat: Optional[int] = Field(
        default=None,
        description="Mirostat sampling strategy. 0=disabled, 1 or 2=enabled with different modes."
    )
    mirostat_tau: Optional[float] = Field(
        default=None,
        description="Tau parameter for Mirostat sampling. Typically 5.0 or 0.8."
    )
    mirostat_eta: Optional[float] = Field(
        default=None,
        description="Eta parameter for Mirostat sampling."
    )
    penalize_newline: Optional[bool] = Field(
        default=None,
        description="Whether to penalize newline tokens."
    )
    stop: Optional[List[str]] = Field(
        default=None,
        description="List of strings that stop generation."
    )
    numa: Optional[bool] = Field(
        default=None,
        description="Whether to use NUMA (advanced hardware setting)."
    )
    num_ctx: Optional[int] = Field(
        default=None,
        description="Size of the context window in tokens."
    )
    num_batch: Optional[int] = Field(
        default=None,
        description="Batch size for generation tokens. Typically 512 or 1024."
    )
    num_gpu: Optional[int] = Field(
        default=None,
        description="How many GPUs to use for inference if available."
    )
    main_gpu: Optional[int] = Field(
        default=None,
        description="Which GPU to treat as the primary for multi-GPU usage."
    )
    low_vram: Optional[bool] = Field(
        default=None,
        description="Attempt to use less VRAM, can slow inference."
    )
    vocab_only: Optional[bool] = Field(
        default=None,
        description="If True, only load the vocabulary of the model."
    )
    use_mmap: Optional[bool] = Field(
        default=None,
        description="Use memory-mapped files for the model."
    )
    use_mlock: Optional[bool] = Field(
        default=None,
        description="Use mlock to lock memory. Prevents swapping, requires privileges."
    )
    num_thread: Optional[int] = Field(
        default=None,
        description="Number of CPU threads to use for inference."
    )
    
class GenerateRequest(BaseModel):
    """
    Request body for /api/generate endpoint.
    """
    model: str = Field(
        ...,
        description="Name of the model to use, e.g. 'llama3.2'"
    )
    prompt: Optional[str] = Field(
        default=None,
        description="Prompt for text generation."
    )
    suffix: Optional[str] = Field(
        default=None,
        description="Text that comes after the model response, appended to the generation."
    )
    images: Optional[List[str]] = Field(
        default=None,
        description="List of base64-encoded images for multimodal models (e.g., llava)."
    )
    format: Optional[Union[str, Dict[str, Any]]] = Field(
        default=None,
        description=(
            "Response format. If a string, can be 'json' or 'jsonschema'. "
            "If a dict, must be a valid JSON Schema or similar."
        )
    )
    options: Optional[GenerateOptions] = Field(
        default=None,
        description="Advanced generation parameters (temperature, seed, etc.)."
    )
    system: Optional[str] = Field(
        default=None,
        description="System message to override what's defined in the model file."
    )
    template: Optional[str] = Field(
        default=None,
        description="Prompt template to override what's defined in the model file."
    )
    stream: Optional[bool] = Field(
        default=True,
        description="If False, the entire response is returned in one object, not a stream."
    )
    raw: Optional[bool] = Field(
        default=False,
        description="If True, bypass the model's templating system and use the prompt as-is."
    )
    keep_alive: Optional[str] = Field(
        default="5m",
        description="Controls how long the model remains loaded after the request. e.g. '5m'."
    )
    context: Optional[List[int]] = Field(
        default=None,
        description="Short conversation context from a previous /generate call (deprecated)."
    )
    
class GenerateResponse(BaseModel):
    """
    Final response object from /api/generate (when streaming finishes).
    """
    model: Optional[str] = Field(
        default=None,
        description="Name of the model used."
    )
    created_at: Optional[str] = Field(
        default=None,
        description="Timestamp in RFC3339/ISO format."
    )
    response: Optional[str] = Field(
        default=None,
        description=(
            "If stream=True, this might be empty in the final chunk, because response "
            "was streamed in chunks. If stream=False, this contains the full response."
        )
    )
    done: Optional[bool] = Field(
        default=False,
        description="Indicates whether the generation has completed."
    )
    context: Optional[List[int]] = Field(
        default=None,
        description="Encoded conversation context you can reuse in a next request."
    )
    total_duration: Optional[int] = Field(
        default=None,
        description="Total time spent on generation (nanoseconds)."
    )
    load_duration: Optional[int] = Field(
        default=None,
        description="Time spent loading the model (nanoseconds)."
    )
    prompt_eval_count: Optional[int] = Field(
        default=None,
        description="Number of tokens in the prompt."
    )
    prompt_eval_duration: Optional[int] = Field(
        default=None,
        description="Time spent evaluating the prompt (nanoseconds)."
    )
    eval_count: Optional[int] = Field(
        default=None,
        description="Number of tokens in the response."
    )
    eval_duration: Optional[int] = Field(
        default=None,
        description="Time spent generating the response (nanoseconds)."
    )
    

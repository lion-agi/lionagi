class EmbedRequest(BaseModel):
    model: str = Field(
        ...,
        description="Name of the model to generate embeddings from."
    )
    input: Union[str, List[str]] = Field(
        ...,
        description="Text or list of text for which to generate embeddings."
    )
    truncate: Optional[bool] = Field(
        default=True,
        description="If True, truncate text that exceeds context length. If False, raises an error."
    )
    options: Optional[GenerateOptions] = Field(
        default=None,
        description="Additional model parameters if needed."
    )
    keep_alive: Optional[str] = Field(
        default="5m",
        description="How long to keep the model in memory, e.g. '5m'."
    )
    
    
class EmbedResponse(BaseModel):
    model: str = Field(
        ...,
        description="Name of the model used for embeddings."
    )
    embeddings: List[List[float]] = Field(
        ...,
        description="List of embeddings. Each sub-list is the vector for one input."
    )
    total_duration: Optional[int] = Field(
        default=None,
        description="Total time spent generating embeddings (nanoseconds)."
    )
    load_duration: Optional[int] = Field(
        default=None,
        description="Time spent loading the model (nanoseconds)."
    )
    prompt_eval_count: Optional[int] = Field(
        default=None,
        description="Number of tokens in the prompt or input text."
    )
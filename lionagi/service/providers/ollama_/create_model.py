class CreateModelRequest(BaseModel):
    """
    Request body for creating a new model, possibly from an existing model, safetensors,
    or a GGUF file.
    """
    model: str = Field(
        ...,
        description="Name of the new model to create (e.g., 'mario')."
    )
    from_: Optional[str] = Field(
        default=None,
        alias="from",
        description="Name of an existing model to clone or base from."
    )
    files: Optional[Dict[str, str]] = Field(
        default=None,
        description="Map of filename -> SHA256 digest for any uploaded safetensors or GGUF files."
    )
    adapters: Optional[Dict[str, str]] = Field(
        default=None,
        description="Map of LORA adapter filename -> SHA256 digest."
    )
    template: Optional[str] = Field(
        default=None,
        description="Prompt template for the new model."
    )
    license: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="License string or list of licenses for the new model."
    )
    system: Optional[str] = Field(
        default=None,
        description="System prompt that overrides defaults for the new model."
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional parameters for the new model (key-value)."
    )
    messages: Optional[List[ChatMessage]] = Field(
        default=None,
        description="List of messages if you want to store conversation data in the model."
    )
    stream: Optional[bool] = Field(
        default=True,
        description="If False, returns a single JSON object instead of streaming statuses."
    )
    quantize: Optional[str] = Field(
        default=None,
        description="Quantization type, e.g. 'q4_K_M'. Only applies if the base model is float16."
    )
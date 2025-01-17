class LocalModelDetails(BaseModel):
    format: Optional[str] = Field(
        default=None,
        description="File format, e.g. 'gguf'."
    )
    family: Optional[str] = Field(
        default=None,
        description="Primary family (like 'llama')."
    )
    families: Optional[List[str]] = Field(
        default=None,
        description="Other families/tags associated with this model."
    )
    parameter_size: Optional[str] = Field(
        default=None,
        description="Number of parameters in the model, e.g. '13B'."
    )
    quantization_level: Optional[str] = Field(
        default=None,
        description="Quantization detail, e.g. 'Q4_0'."
    )
    
class LocalModelInfo(BaseModel):
    """
    Each item in the list of local models.
    """
    name: str = Field(..., description="Full name of the model, e.g. 'llama3:latest'.")
    modified_at: Optional[str] = Field(
        default=None,
        description="Last modification timestamp in RFC3339/ISO format."
    )
    size: Optional[int] = Field(
        default=None,
        description="File size in bytes."
    )
    digest: Optional[str] = Field(
        default=None,
        description="SHA256 digest of the model."
    )
    details: Optional[LocalModelDetails] = Field(
        default=None,
        description="Additional metadata about the model."
    )
    
class ListLocalModelsResponse(BaseModel):
    models: List[LocalModelInfo] = Field(
        ...,
        description="List of locally available models."
    )
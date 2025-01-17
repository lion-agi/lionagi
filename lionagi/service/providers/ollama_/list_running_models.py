class RunningModelDetails(BaseModel):
    parent_model: Optional[str] = Field(
        default=None,
        description="If this model was derived from another model, its parent is shown here."
    )
    format: Optional[str] = Field(
        default=None,
        description="Storage format (gguf, etc.)."
    )
    family: Optional[str] = Field(
        default=None,
        description="Primary family (like 'llama')."
    )
    families: Optional[List[str]] = Field(
        default=None,
        description="All families/tags that apply."
    )
    parameter_size: Optional[str] = Field(
        default=None,
        description="Parameter count in e.g. '7B', '13B'."
    )
    quantization_level: Optional[str] = Field(
        default=None,
        description="Quantization detail, e.g. 'Q4_0'."
    )


class RunningModelInfo(BaseModel):
    name: str = Field(
        ...,
        description="Model name with optional tag, e.g. 'mistral:latest'."
    )
    model: str = Field(
        ...,
        description="Exact model path or reference."
    )
    size: Optional[int] = Field(
        default=None,
        description="File size in bytes loaded into memory."
    )
    digest: Optional[str] = Field(
        default=None,
        description="SHA256 digest of the model's data."
    )
    details: Optional[RunningModelDetails] = Field(
        default=None,
        description="Detailed metadata of the running model."
    )
    expires_at: Optional[str] = Field(
        default=None,
        description="When the keep_alive will unload this model from memory, if any."
    )
    size_vram: Optional[int] = Field(
        default=None,
        description="VRAM usage of the model in bytes, if using GPU."
    )
    
    
class ListRunningModelsResponse(BaseModel):
    models: List[RunningModelInfo] = Field(
        ...,
        description="List of currently loaded models."
    )
class ShowModelRequest(BaseModel):
    model: str = Field(
        ...,
        description="Name of the model to show, e.g. 'llama3.2'."
    )
    verbose: Optional[bool] = Field(
        default=False,
        description="If True, returns more verbose info like merges, token types, etc."
    )
    
class ShowModelResponse(BaseModel):
    modelfile: Optional[str] = Field(
        default=None,
        description="Raw Modelfile as stored in Ollama."
    )
    parameters: Optional[str] = Field(
        default=None,
        description="Parameter details in text form."
    )
    template: Optional[str] = Field(
        default=None,
        description="Prompt template used by the model."
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadata about the model (format, family, quant, etc.)."
    )
    model_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed internal data, e.g. architecture, block counts, etc."
    )
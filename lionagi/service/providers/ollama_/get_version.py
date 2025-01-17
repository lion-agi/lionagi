class VersionResponse(BaseModel):
    version: str = Field(
        ...,
        description="The version string of the Ollama server."
    )
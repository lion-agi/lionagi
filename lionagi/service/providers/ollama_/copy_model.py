class CopyModelRequest(BaseModel):
    source: str = Field(
        ...,
        description="Name of the existing model to copy."
    )
    destination: str = Field(
        ...,
        description="Name of the new model to create."
    )
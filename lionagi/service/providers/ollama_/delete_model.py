class DeleteModelRequest(BaseModel):
    model: str = Field(
        ...,
        description="Name of the model to delete."
    )
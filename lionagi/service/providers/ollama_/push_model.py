class PushModelRequest(BaseModel):
    model: str = Field(
        ...,
        description="Name of the model to push, e.g. 'mattw/pygmalion:latest'."
    )
    insecure: Optional[bool] = Field(
        default=False,
        description="Allow insecure connections (dev/test usage)."
    )
    stream: Optional[bool] = Field(
        default=True,
        description="If False, returns a single JSON object on completion."
    )
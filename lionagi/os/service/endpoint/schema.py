from pydantic import BaseModel, ConfigDict


class EndpointSchema(BaseModel):
    endpoint: str
    pricing: tuple
    batch_pricing: tuple
    token_limit: int
    default_config: dict
    default_rate_limit: tuple  # (interval, interval_request, interval_token)
    required_params: list[str] = []
    optional_params: list[str] = []
    input_key: str

    model_config = ConfigDict(
        arbitrary_types_allowed=True, populate_by_name=True, extra="forbid"
    )

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, **data):
        return cls(**data)

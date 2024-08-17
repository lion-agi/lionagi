from pydantic import BaseModel, ConfigDict
from lionagi.os.service.utils import create_payload


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

    def create_payload(self, input_):
        return create_payload(
            input_=input_,
            input_key=self.input_key,
            config=self.default_config,
            required_=self.required_params,
            optional_=self.optional_params,
        )


class ModelConfig(BaseModel):
    model: str
    alias: list[str]
    endpoint_schema: dict[str, EndpointSchema]

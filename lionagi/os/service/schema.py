from pydantic import BaseModel, ConfigDict
from lionagi.os.service.utils import create_payload


class SchemaModel(BaseModel):

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, **data):
        return cls(**data)


class EndpointSchema(SchemaModel):
    endpoint: str
    pricing: tuple | float = None
    batch_pricing: tuple | float = None
    token_limit: int
    default_config: dict
    default_rate_limit: tuple = (
        None,
        None,
        None,
        None,
        None,
    )  # (interval, interval_request, interval_token, refresh_time, concurrent_capacity)
    required_params: list[str] = []
    optional_params: list[str] = []
    input_key: str | list[str]
    image_pricing: dict = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="forbid",
    )

    def create_payload(self, input_):
        return create_payload(
            input_=input_,
            input_key=self.input_key,
            config=self.default_config,
            required_=self.required_params,
            optional_=self.optional_params,
        )


class ModelConfig(SchemaModel):
    model: str
    alias: list[str]
    endpoint_schema: dict[str, EndpointSchema]

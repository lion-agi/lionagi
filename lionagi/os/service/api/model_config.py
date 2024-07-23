from pydantic import BaseModel


class ENDPOINT_CONFIG(BaseModel):
    endpoint: str
    pricing: tuple
    batch_pricing: tuple
    token_limit: int
    default_config: dict
    default_rate_limit: tuple
    required_params: list[str] = []
    optional_params: list[str] = []
    input_key: str


class MODEL_CONFIG(BaseModel):
    model: str
    alias: list[str]                        # list of aliases for pricing and token limit
    endpoint_schema: dict[ENDPOINT_CONFIG]  # list of supported endpoints    


class PROVIDER_CONFIG(BaseModel):
    api_key_scheme: str
    provider: str
    models: dict[MODEL_CONFIG]  # list of supported models
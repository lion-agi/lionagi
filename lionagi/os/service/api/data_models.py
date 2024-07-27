from pydantic import BaseModel


class MODEL_CONFIG(BaseModel):
    model: str
    alias: list[str]  # list of aliases for pricing and token limit
    endpoint_schema: dict[
        str, ENDPOINT_CONFIG
    ]  # dict of supported endpoints  {endpoint: ENDPOINT_CONFIG}


class PROVIDER_CONFIG(BaseModel):
    api_key_scheme: dict
    provider: str
    base_url: str

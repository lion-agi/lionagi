from abc import abstractmethod
from typing import Any
from typing_extensions import override

from lion_core.setting import SchemaModel, RetryConfig
from pydantic import Field

from lionagi.os.service.utils import create_payload


class RateLimitConfig(SchemaModel):
    interval: int
    interval_request: int
    interval_token: int
    refresh_time: int
    concurrent_capacity: int


class CachedConfig(SchemaModel):
    ttl: int
    key: str | None
    namespace: str | None
    key_builder: str | None
    skip_cache_func: callable = lambda x: False
    serializer: str | str
    plugins: list | None
    alias: str | None
    noself: callable = lambda x: False


class VisionPricingSchema(SchemaModel):
    base_cost: int
    low_detail_cost: int = 0
    max_dimension: int = 2048
    min_side: int = 768
    square_size: int
    square_cost: int


class ModelPricingSchema(SchemaModel):
    model: str
    input_price: float
    output_price: float | None = None
    training_price: float | None = None
    batch_input_price: float | None = None
    batch_output_price: float | None = None
    vision_pricing: VisionPricingSchema | None = None
    audio_pricing: SchemaModel | None = None


class ModelSpecSchema(SchemaModel):
    model: str
    model_pricing: ModelPricingSchema
    model_token_limit: int
    model_alias: list[str]
    model_default_endpoint: str
    model_default_rate_limit: RateLimitConfig
    model_token_limit: int
    model_default_params: dict

    @override
    def update(self, new_schema_obj: bool = False, **kwargs):
        mprice = self.model_pricing.update(new_schema_obj=True, **kwargs)
        mlimit = self.model_default_rate_limit.update(new_schema_obj=True, **kwargs)
        mparams = self.model_default_params.copy()
        for i in kwargs:
            if i in mparams:
                mparams[i] = kwargs[i]
        kwargs["model_pricing"] = mprice
        kwargs["model_default_rate_limit"] = mlimit
        kwargs["model_default_params"] = mparams
        return super().update(new_schema_obj=new_schema_obj, **kwargs)


class BaseEndpointSchema(SchemaModel):
    base_url: str
    endpoint: str
    required_params: list[str] = []
    optional_params: list[str] = []
    api_key: str | None = Field(None, exclude=True)
    api_key_schema: str | None = Field(None, exclude=True)
    retry_config: RetryConfig

    @abstractmethod
    def create_payload(self, input_: Any):
        pass

    @property
    def request_url(self):
        return f"{self.base_url}/{self.endpoint}"


class TokenRateLimitedEndpointSchema(BaseEndpointSchema):
    model_spec_config: ModelSpecSchema
    rate_limit_config: RateLimitConfig
    payload_input_key: str | list[str]

    @property
    def model(self):
        return self.model_spec_config.model

    @property
    def model_params(self):
        params = self.model_spec_config.model_default_params.copy()
        params["model"] = params.get("model", self.model)
        return params

    @override
    def update(self, new_schema_obj: bool = False, **kwargs):
        ms = self.model_spec_config.update(new_schema_obj=True, **kwargs)
        rl = self.rate_limit_config.update(new_schema_obj=True, **kwargs)
        rc = self.retry_config.update(new_schema_obj=True, **kwargs)
        kwargs["model_spec_config"] = ms
        kwargs["rate_limit_config"] = rl
        kwargs["retry_config"] = rc
        return super().update(new_schema_obj=new_schema_obj, **kwargs)

    def create_payload(self, input_: Any):
        return create_payload(
            payload_input=input_,
            payload_input_key=self.payload_input_key,
            payload_config=self.model_params,
            required_params=self.required_params,
            optional_params=self.optional_params,
        )

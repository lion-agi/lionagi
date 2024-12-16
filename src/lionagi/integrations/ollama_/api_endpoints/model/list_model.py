from typing import List

from pydantic import BaseModel, Field

from ..data_models import OllamaEndpointResponseBody


class Detail(BaseModel):
    parent_model: str = Field(None)

    format: str = Field(None)

    family: str = Field(None)

    families: list[str] | None = Field(None)

    parameter_size: str = Field(None)

    quantization_level: str = Field(None)


class LocalModel(BaseModel):
    name: str = Field(None)

    model: str = Field(None)

    modified_at: str = Field(None)

    size: int = Field(None)

    digest: str = Field(None)

    details: Detail = Field(None)


class OllamaListLocalModelsResponseBody(OllamaEndpointResponseBody):
    models: list[LocalModel] = Field(None)


class RunningModel(BaseModel):
    name: str = Field(None)

    model: str = Field(None)

    size: int = Field(None)

    digest: str = Field(None)

    details: Detail = Field(None)

    expires_at: str = Field(None)

    size_vram: int = Field(None)


class OllamaListRunningModelsResponseBody(OllamaEndpointResponseBody):
    models: list[RunningModel] = Field(None)

from abc import ABC

from pydantic import BaseModel
from lionagi.os.file.tokenize.token_calculator import ProviderTokenCalculator
from .specification import MODEL_CONFIG
from .base_service import BaseService


class PROVIDER_CONFIG(BaseModel):
    api_key_scheme: dict
    provider: str
    base_url: str


class PROVIDER_MODEL_SPECIFICATION(BaseModel):
    models: dict[str, MODEL_CONFIG]


class Provider(ABC):

    token_calculator: ProviderTokenCalculator = None
    config: PROVIDER_CONFIG = None
    model_specification: PROVIDER_MODEL_SPECIFICATION = None
    service: BaseService = None

from abc import ABC
from typing import Type

from lionagi.os.file.tokenize.token_calculator import ProviderTokenCalculator
from lionagi.os.service.api.data_models import PROVIDER_CONFIG, MODEL_CONFIG
from lionagi.os.service.api.base_service import BaseService
from lionagi.os.service.api.endpoint import EndPoint


class Provider(ABC):

    token_calculator: ProviderTokenCalculator = None
    config: PROVIDER_CONFIG = None

    # dict of supported models {model: MODEL_CONFIG}
    model_specification: dict[str, MODEL_CONFIG]
    service_class: Type[BaseService] = None
    service: dict[str, BaseService] = None

    @classmethod
    def find_token_limit(cls, model, endpoint: str | EndPoint):
        return cls.get_endpoint_config(model, endpoint).token_limit

    @classmethod
    def calculate_tokens(cls, endpoint: str, payload: dict, image_base64):
        return cls.token_calculator.calculate(endpoint, payload, image_base64)

    @classmethod
    def get_endpoint_config(cls, model, endpoint: str | EndPoint):
        if isinstance(endpoint, EndPoint):
            endpoint = endpoint.endpoint
        return cls.model_specification[model].endpoint_schema[endpoint]

    @classmethod
    def new_service(cls, *args, **kwargs):
        service = cls.service_class(*args, **kwargs)

        ...

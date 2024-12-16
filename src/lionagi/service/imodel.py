import warnings

from lionagi.service.service import Service
from lionagi.service.service_match_util import (
    match_parameters,
    match_service,
    match_task_method,
)


class iModel:
    def __init__(
        self,
        provider: str | Service,
        task: str = "chat",
        model: str = None,
        api_key: str = None,
        api_key_schema: str = None,
        interval_tokens: int = None,
        interval_requests: int = None,
        **kwargs,
    ):
        if api_key is not None:
            api_key = api_key
        elif api_key_schema is not None:
            api_key = api_key_schema

        # Deprecation
        if "config" in kwargs:
            warnings.warn(
                "'config' is deprecated in 'iModel'. Please pass configurations directly as keyword arguments. "
                "If 'config' is a parameter name for further request settings, it will still be passed along.",
                DeprecationWarning,
                stacklevel=2,
            )
        if "provider_schema" in kwargs:
            warnings.warn(
                "'provider_schema' is deprecated in 'iModel'. Please refer to the corresponding service's "
                "Pydantic models for the schema structure. "
                "If 'provider_schema' is a parameter name for further request settings, it will still be passed along.",
                DeprecationWarning,
                stacklevel=2,
            )
        if "endpoint" in kwargs:
            warnings.warn(
                "'endpoint' is deprecated in 'iModel'. Please specify 'task' instead. "
                "If 'endpoint' is a parameter name for further request settings, it will still be passed along.",
                DeprecationWarning,
                stacklevel=2,
            )
            task = kwargs["endpoint"]
        if "token_encoding_name" in kwargs:
            warnings.warn(
                "'token_encoding_name' is deprecated in 'iModel' as it is now automatically detected. "
                "To explicitly set the encoding method, please refer to TokenCalculator.",
                DeprecationWarning,
                stacklevel=2,
            )
        if "interval" in kwargs:
            warnings.warn(
                "'interval' is deprecated in 'iModel' as the unit is now set per minute. "
                "If 'interval' is a parameter name for further request settings, it will still be passed along.",
                DeprecationWarning,
                stacklevel=2,
            )
        if "service" in kwargs:
            warnings.warn(
                "'service' parameter is deprecated in 'iModel'. Please use 'provider' instead. For more "
                "details about service configurations, refer to 'lion.service' or the corresponding service's package. "
                "If 'service' is a parameter name for further request settings, it will still be passed along.",
                DeprecationWarning,
                stacklevel=2,
            )
        if "allowed_parameters" in kwargs:
            warnings.warn(
                "'allowed_parameters' is deprecated in 'iModel'. If 'allowed_parameters' is a parameter "
                "name for further request settings, it will still be passed along.",
                DeprecationWarning,
                stacklevel=2,
            )
        if "device" in kwargs:
            warnings.warn(
                "'device' is deprecated in 'iModel'. "
                "If 'device' is a parameter name for further request settings, it will still be passed along.",
                DeprecationWarning,
                stacklevel=2,
            )
        if "costs" in kwargs:
            warnings.warn(
                "'cost' is deprecated in 'iModel'. "
                "If 'costs' is a parameter name for further request settings, it will still be passed along.",
                DeprecationWarning,
                stacklevel=2,
            )

        if isinstance(provider, str):
            self.service = match_service(provider, api_key=api_key, **kwargs)
        elif isinstance(provider, Service):
            self.service = provider
            if api_key:
                warnings.warn(
                    "A Service instance was provided along with api key info."
                    "The the separately provided api_key or api_key_schema will be ignored."
                )
        else:
            raise ValueError(
                "Invalid provider. Please provide a valid provider name or valid service object."
            )

        task_method_list = match_task_method(task, self.service)
        if len(task_method_list) == 0:
            raise ValueError(
                "No matching task found. "
                "Please refer to the service provider's API to provide a valid task."
            )
        if len(task_method_list) > 1:
            raise ValueError(
                f"Multiple possible tasks found. Please specify: {task_method_list}"
            )
        self.task = task_method_list[0]
        task_method = getattr(self.service, task_method_list[0])
        task_params = match_parameters(
            task_method, model, interval_tokens, interval_requests
        )
        try:
            self.request_model = task_method(**task_params)
        except Exception as e:
            raise ValueError(
                f"{self.task} requires the following to be provided as input: {e}."
            )

        self.model = model
        self.configs = kwargs

        self.data_model = self.service.match_data_model(self.task)

    def parse_to_data_model(self, **kwargs):
        if kwargs.get("model") and self.model:
            if kwargs.get("model") != self.model:
                raise ValueError(
                    f"Models are inconsistent. This iModel is for {self.model}"
                )

        output = {}
        for invoke_param, data_model in self.data_model.items():
            data_model_dict = {}
            if "model" in data_model.model_fields:
                data_model_dict["model"] = self.model
            for key in self.configs:
                if key in data_model.model_fields:
                    data_model_dict[key] = self.configs[key]
            for key in kwargs:
                if key in data_model.model_fields:
                    data_model_dict[key] = kwargs[key]
            output[invoke_param] = data_model(**data_model_dict)
        return output

    async def invoke(self, **kwargs):
        return await self.request_model.invoke(**kwargs)

    def list_tasks(self):
        return self.service.list_tasks()


__all__ = ["iModel"]

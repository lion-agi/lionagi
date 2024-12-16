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

        if task == "chat":
            match provider:
                case "openai":
                    task = "create_chat_completion"
                case "anthropic":
                    task = "create_message"
                case "groq":
                    task = "create_chat_completion"
                case "perplexity":
                    task = "create_chat_completion"

        if isinstance(provider, str):
            if api_key is None:
                match provider:
                    case "openai":
                        api_key = "OPENAI_API_KEY"
                    case "anthropic":
                        api_key = "ANTHROPIC_API_KEY"
                    case "groq":
                        api_key = "GROQ_API_KEY"
                    case "perplexity":
                        api_key = "PERPLEXIY_API_KEY"

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

    @property
    def allowed_roles(self):
        return self.service.allowed_roles


__all__ = ["iModel"]

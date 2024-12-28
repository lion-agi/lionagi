import inspect
import json
import os
import warnings
from pathlib import Path

import litellm

from lionagi.service.service import Service

litellm.drop_params = True


class iModel:

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.rate_limiter = None

    @classmethod
    def list_tasks(cls):
        methods = []
        for name, member in inspect.getmembers(
            cls, predicate=inspect.isfunction
        ):
            if name not in [
                "__init__",
                "__setattr__",
                "check_rate_limiter",
                "match_data_model",
            ]:
                methods.append(name)
        return methods

    async def speech_to_text(self, file: str | Path, **kwargs):
        from litellm import atranscription

        audio_file = open(file, "rb")
        kwargs.update(self.kwargs)
        return await atranscription(file=audio_file, **kwargs)

    async def text_to_speech(
        self, input_: str, speech_file_path: Path, **kwargs
    ):
        pass

    async def chat(self, messages: list, **kwargs):
        from litellm import acompletion

        kwargs.update(self.kwargs)
        return await acompletion(messages=messages, **kwargs)

    # Chat
    def create_chat_completion(
        self, model: str, limit_tokens: int = None, limit_requests: int = None
    ):
        model_obj = OpenAIModel(
            model=model,
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="chat/completions",
            method="POST",
            content_type="application/json",
            limit_tokens=limit_tokens,
            limit_requests=limit_requests,
        )

        return self.check_rate_limiter(
            model_obj, limit_requests=limit_requests, limit_tokens=limit_tokens
        )

    # Embeddings
    def create_embeddings(
        self, model: str, limit_tokens: int = None, limit_requests: int = None
    ):
        model_obj = OpenAIModel(
            model=model,
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="embeddings",
            method="POST",
            content_type="application/json",
            limit_tokens=limit_tokens,
            limit_requests=limit_requests,
        )
        return self.check_rate_limiter(
            model_obj, limit_requests=limit_requests, limit_tokens=limit_tokens
        )

    # Fine_tuning
    def create_fine_tuning_job(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="fine_tuning/jobs",
            method="POST",
            content_type="application/json",
        )

    def list_fine_tuning_jobs(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="fine_tuning/jobs",
            method="GET",
        )

    def list_fine_tuning_events(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="fine_tuning/jobs/{fine_tuning_job_id}/events",
            method="GET",
        )

    def list_fine_tuning_checkpoints(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="fine_tuning/jobs/{fine_tuning_job_id}/checkpoints",
            method="GET",
        )

    def retrieve_fine_tuning_job(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="fine_tuning/jobs/{fine_tuning_job_id}",
            method="GET",
        )

    def cancel_fine_tuning(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="fine_tuning/jobs/{fine_tuning_job_id}/cancel",
            method="POST",
        )

    # Batch
    def create_batch(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="batches",
            method="POST",
            content_type="application/json",
        )

    def retrieve_batch(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="batches/{batch_id}",
            method="GET",
            content_type="application/json",
        )

    def cancel_batch(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="batches/{batch_id}/cancel",
            method="POST",
            content_type="application/json",
        )

    def list_batch(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="batches",
            method="GET",
            content_type="application/json",
        )

    # Files
    def upload_file(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="files",
            method="POST",
        )

    def list_files(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="files",
            method="GET",
        )

    def retrieve_file(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="files/{file_id}",
            method="GET",
        )

    def delete_file(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="files/{file_id}",
            method="DELETE",
        )

    def retrieve_file_content(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="files/{file_id}/content",
            method="GET",
        )

    # Uploads
    def create_upload(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="uploads",
            method="POST",
        )

    def add_upload_part(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="uploads/{upload_id}/parts",
            method="POST",
        )

    def complete_upload(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="uploads/{upload_id}/complete",
            method="POST",
        )

    def cancel_upload(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="uploads/{upload_id}/cancel",
            method="POST",
        )

    # Images
    def create_image(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="images/generations",
            method="POST",
            content_type="application/json",
        )

    def create_image_edit(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="images/edits",
            method="POST",
        )

    def create_image_variation(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="images/variations",
            method="POST",
        )

    # Models
    def list_models(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="models",
            method="GET",
        )

    def retrieve_model(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="models/{model}",
            method="GET",
        )

    def delete_fine_tuned_model(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="models/{model}",
            method="DELETE",
        )

    # Moderations
    def create_moderation(self):
        return OpenAIRequest(
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="moderations",
            method="POST",
            content_type="application/json",
        )


class iModel:

    def __init__(
        self,
        provider: str | Service | None = None,
        model: str = None,
        api_key: str = None,
        api_key_schema: str = None,
        interval_tokens: int = None,
        interval_requests: int = None,
        **kwargs,
    ): ...

    def __init__(self, **kwargs):
        if "api_key" in kwargs:
            try:
                api_key1 = os.getenv(kwargs["api_key"], None)
                if api_key1:
                    # Store the original env var name as schema
                    self.api_key_schema = kwargs["api_key"]
                    # Store the resolved value for actual use
                    kwargs["api_key"] = api_key1
            except Exception:
                pass
        self.kwargs = kwargs
        self.acompletion = self.litellm.acompletion

    def to_dict(self) -> dict:
        dict_ = {
            k: v for k, v in self.kwargs.items() if k not in RESERVED_PARAMS
        }
        # If we have an api_key_schema, use that instead of the resolved value
        if hasattr(self, "api_key_schema"):
            dict_["api_key"] = self.api_key_schema
        return dict_

    @classmethod
    def from_dict(cls, data: dict) -> "LiteiModel":
        return cls(**data)

    async def invoke(self, **kwargs):
        config = {**self.kwargs, **kwargs}
        for i in RESERVED_PARAMS:
            config.pop(i, None)

        return await self.acompletion(**config)

    def __hash__(self):
        # Convert kwargs to a hashable format by serializing unhashable types
        hashable_items = []
        for k, v in self.kwargs.items():
            if isinstance(v, (list, dict)):
                # Convert unhashable types to JSON string for hashing
                v = json.dumps(v, sort_keys=True)
            elif not isinstance(v, (str, int, float, bool, type(None))):
                # Convert other unhashable types to string representation
                v = str(v)
            hashable_items.append((k, v))
        return hash(frozenset(hashable_items))

    @property
    def allowed_roles(self):
        return ["user", "assistant", "system"]

    @property
    def sequential_exchange(self):
        """whether the service requires user/assistant exchange"""
        return False

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

    @property
    def sequential_exchange(self):
        """whether the service requires user/assistant exchange"""
        return self.service.sequential_exchange


__all__ = ["iModel"]

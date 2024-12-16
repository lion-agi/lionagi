import inspect

from dotenv import load_dotenv

from lionagi.service import Service, register_service

from .api_endpoints.api_request import OpenAIRequest
from .api_endpoints.match_data_model import match_data_model
from .OpenAIModel import OpenAIModel

load_dotenv()


@register_service
class OpenAIService(Service):
    def __init__(
        self,
        api_key: str,
        openai_organization: str = None,
        openai_project: str = None,
        name: str = None,
    ):
        super().__setattr__("_initialized", False)
        self.api_key = api_key
        self.openai_organization = openai_organization
        self.openai_project = openai_project
        self.name = name
        self.rate_limiters = {}  # model: RateLimiter
        super().__setattr__("_initialized", True)

    def __setattr__(self, key, value):
        if getattr(self, "_initialized", False) and key in [
            "api_key",
            "openai_organization",
            "openai_project",
        ]:
            raise AttributeError(
                f"Cannot modify '{key}' after initialization. "
                f"Please set a new service object for new keys."
            )
        super().__setattr__(key, value)

    def check_rate_limiter(
        self,
        openai_model: OpenAIModel,
        limit_requests: int = None,
        limit_tokens: int = None,
    ):
        shared_models = {
            "gpt-4-turbo-2024-04-09": "gpt-4-turbo",
            "gpt-4-turbo-preview": "gpt-4-turbo",
            "gpt-4-0125-preview": "gpt-4-turbo",
            "gpt-4-1106-preview": "gpt-4-turbo",
            "gpt-4o-2024-05-13": "gpt-4o",
            "gpt-4o-2024-08-06": "gpt-4o",
            "gpt-4o-mini-2024-07-18": "gpt-4o-mini",
        }

        if openai_model.model in shared_models:
            model = shared_models[openai_model.model]
        else:
            model = openai_model.model

        if model not in self.rate_limiters:
            self.rate_limiters[model] = openai_model.rate_limiter
        else:
            openai_model.rate_limiter = self.rate_limiters[model]
            if limit_requests:
                openai_model.rate_limiter.limit_requests = limit_requests
            if limit_tokens:
                openai_model.rate_limiter.limit_tokens = limit_tokens

        return openai_model

    @staticmethod
    def match_data_model(task_name):
        return match_data_model(task_name)

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

    # Audio
    def create_speech(self, model: str, limit_requests: int = None):
        model_obj = OpenAIModel(
            model=model,
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="audio/speech",
            method="POST",
            content_type="application/json",
            limit_requests=limit_requests,
        )

        return self.check_rate_limiter(
            model_obj, limit_requests=limit_requests
        )

    def create_transcription(self, model: str, limit_requests: int = None):
        model_obj = OpenAIModel(
            model=model,
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="audio/transcriptions",
            method="POST",
            limit_requests=limit_requests,
        )

        return self.check_rate_limiter(
            model_obj, limit_requests=limit_requests
        )

    def create_translation(self, model: str, limit_requests: int = None):
        model_obj = OpenAIModel(
            model=model,
            api_key=self.api_key,
            openai_organization=self.openai_organization,
            openai_project=self.openai_project,
            endpoint="audio/translations",
            method="POST",
            limit_requests=limit_requests,
        )

        return self.check_rate_limiter(
            model_obj, limit_requests=limit_requests
        )

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

# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect

from dotenv import load_dotenv

from lionagi.service import Service, register_service

from .api_endpoints.data_models import (
    GroqAudioRequest,
    GroqChatCompletionRequest,
)
from .GroqModel import GroqModel

load_dotenv()


@register_service
class GroqService(Service):
    def __init__(
        self,
        api_key: str,
        name: str | None = None,
    ):
        """Initialize the Groq service."""
        super().__setattr__("_initialized", False)
        self.api_key = api_key
        self.name = name
        self.rate_limiters = {}  # model: RateLimiter
        super().__setattr__("_initialized", True)

    def __setattr__(self, key, value):
        """Prevent modification of critical attributes after initialization."""
        if getattr(self, "_initialized", False) and key in ["api_key"]:
            raise AttributeError(
                f"Cannot modify '{key}' after initialization. "
                f"Please create a new service instance for different credentials."
            )
        super().__setattr__(key, value)

    def check_rate_limiter(
        self,
        groq_model: GroqModel,
        limit_requests: int | None = None,
        limit_tokens: int | None = None,
    ) -> GroqModel:
        """Check and update rate limiter for the model."""
        if groq_model.model not in self.rate_limiters:
            if groq_model.rate_limiter:
                self.rate_limiters[groq_model.model] = groq_model.rate_limiter
        else:
            groq_model.rate_limiter = self.rate_limiters[groq_model.model]
            if limit_requests is not None:
                groq_model.rate_limiter.limit_requests = limit_requests
            if limit_tokens is not None:
                groq_model.rate_limiter.limit_tokens = limit_tokens

        return groq_model

    @staticmethod
    def match_data_model(task_name: str) -> dict:
        """Match task name to appropriate request model mapping."""
        if task_name in ["chat/completions", "create_chat_completion"]:
            return {"request_body": GroqChatCompletionRequest}
        elif task_name in ["audio/transcriptions", "create_transcription"]:
            return {"request_body": GroqAudioRequest}
        elif task_name in ["audio/translations", "create_translation"]:
            return {"request_body": GroqAudioRequest}
        raise ValueError(f"Unknown task: {task_name}")

    @classmethod
    def list_tasks(cls) -> list[str]:
        """List available tasks."""
        methods = []
        for name, member in inspect.getmembers(
            cls, predicate=inspect.isfunction
        ):
            if name not in [
                "__init__",
                "__setattr__",
                "check_rate_limiter",
                "match_data_model",
                "list_tasks",
            ]:
                methods.append(name)
        return methods

    # Chat Completions
    def create_chat_completion(
        self,
        model: str,
        limit_tokens: int | None = None,
        limit_requests: int | None = None,
    ) -> GroqModel:
        """Create a chat completion model."""
        model_obj = GroqModel(
            model=model,
            api_key=self.api_key,
            endpoint="chat/completions",
            method="POST",
            content_type="application/json",
        )

        return self.check_rate_limiter(
            model_obj,
            limit_requests=limit_requests,
            limit_tokens=limit_tokens,
        )

    # Audio
    def create_transcription(
        self,
        model: str,
        limit_requests: int | None = None,
    ) -> GroqModel:
        """Create an audio transcription model."""
        model_obj = GroqModel(
            model=model,
            api_key=self.api_key,
            endpoint="audio/transcriptions",
            method="POST",
        )

        return self.check_rate_limiter(
            model_obj,
            limit_requests=limit_requests,
        )

    def create_translation(
        self,
        model: str,
        limit_requests: int | None = None,
    ) -> GroqModel:
        """Create an audio translation model."""
        model_obj = GroqModel(
            model=model,
            api_key=self.api_key,
            endpoint="audio/translations",
            method="POST",
        )

        return self.check_rate_limiter(
            model_obj,
            limit_requests=limit_requests,
        )

    @property
    def allowed_roles(self):
        return ["user", "assistant", "system"]

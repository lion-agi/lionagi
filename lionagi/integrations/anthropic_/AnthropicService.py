# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect

from dotenv import load_dotenv

from lionagi.integrations.anthropic_.api_endpoints.messages.request.request_body import (
    AnthropicMessageRequestBody,
)
from lionagi.service import Service, register_service

from .AnthropicModel import AnthropicModel

load_dotenv()


@register_service
class AnthropicService(Service):
    def __init__(
        self,
        api_key: str,
        api_version: str = "2023-06-01",
        name: str = None,
    ):
        super().__setattr__("_initialized", False)
        self.api_key = api_key
        self.api_version = api_version
        self.name = name
        self.rate_limiters = {}  # model: RateLimiter
        super().__setattr__("_initialized", True)

    def __setattr__(self, key, value):
        if getattr(self, "_initialized", False) and key in [
            "api_key",
            "api_version",
        ]:
            raise AttributeError(
                f"Cannot modify '{key}' after initialization. "
                f"Please set a new service object for new keys."
            )
        super().__setattr__(key, value)

    def check_rate_limiter(
        self,
        anthropic_model: AnthropicModel,
        limit_requests: int = None,
        limit_tokens: int = None,
    ):
        # Map model versions to their base models for shared rate limiting
        shared_models = {
            "claude-3-opus-20240229": "claude-3-opus",
            "claude-3-sonnet-20240229": "claude-3-sonnet",
            "claude-3-haiku-20240307": "claude-3-haiku",
        }

        if anthropic_model.model in shared_models:
            model = shared_models[anthropic_model.model]
        else:
            model = anthropic_model.model

        if model not in self.rate_limiters:
            self.rate_limiters[model] = anthropic_model.rate_limiter
        else:
            anthropic_model.rate_limiter = self.rate_limiters[model]
            if limit_requests:
                anthropic_model.rate_limiter.limit_requests = limit_requests
            if limit_tokens:
                anthropic_model.rate_limiter.limit_tokens = limit_tokens

        return anthropic_model

    @staticmethod
    def match_data_model(task_name: str) -> dict:
        """Match task name to appropriate request and response models."""
        if task_name == "create_message":
            return {"request_body": AnthropicMessageRequestBody}
        raise ValueError(f"No data models found for task: {task_name}")

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

    # Messages
    def create_message(
        self, model: str, limit_tokens: int = None, limit_requests: int = None
    ):
        model_obj = AnthropicModel(
            model=model,
            api_key=self.api_key,
            api_version=self.api_version,
            endpoint="messages",
            method="POST",
            content_type="application/json",
            limit_tokens=limit_tokens,
            limit_requests=limit_requests,
        )

        return self.check_rate_limiter(
            model_obj, limit_requests=limit_requests, limit_tokens=limit_tokens
        )

    @property
    def allowed_roles(self):
        return ["user", "assistant"]

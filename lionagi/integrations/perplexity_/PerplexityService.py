# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect

from dotenv import load_dotenv

from lionagi.integrations.perplexity_.api_endpoints.chat_completions.request.request_body import (
    PerplexityChatCompletionRequestBody,
)
from lionagi.service import Service, register_service

from .PerplexityModel import PerplexityModel

load_dotenv()


@register_service
class PerplexityService(Service):
    def __init__(
        self,
        api_key: str,
        name: str = None,
    ):
        super().__setattr__("_initialized", False)
        self.api_key = api_key
        self.name = name
        self.rate_limiters = {}  # model: RateLimiter
        super().__setattr__("_initialized", True)

    def __setattr__(self, key, value):
        if getattr(self, "_initialized", False) and key in [
            "api_key",
        ]:
            raise AttributeError(
                f"Cannot modify '{key}' after initialization. "
                f"Please set a new service object for new keys."
            )
        super().__setattr__(key, value)

    def check_rate_limiter(
        self,
        perplexity_model: PerplexityModel,
        limit_requests: int = None,
        limit_tokens: int = None,
    ):
        # Map model versions to their base models for shared rate limiting
        shared_models = {
            "llama-3.1-sonar-small-128k-online": "llama-3.1-sonar-small",
            "llama-3.1-sonar-medium-128k-online": "llama-3.1-sonar-medium",
            "llama-3.1-sonar-large-128k-online": "llama-3.1-sonar-large",
        }

        if perplexity_model.model in shared_models:
            model = shared_models[perplexity_model.model]
        else:
            model = perplexity_model.model

        if model not in self.rate_limiters:
            self.rate_limiters[model] = perplexity_model.rate_limiter
        else:
            perplexity_model.rate_limiter = self.rate_limiters[model]
            if limit_requests:
                perplexity_model.rate_limiter.limit_requests = limit_requests
            if limit_tokens:
                perplexity_model.rate_limiter.limit_tokens = limit_tokens

        return perplexity_model

    @staticmethod
    def match_data_model(task_name: str) -> dict:
        """Match task name to appropriate request and response models."""
        if task_name == "create_chat_completion":
            return {"request_body": PerplexityChatCompletionRequestBody}
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

    # Chat Completions
    def create_chat_completion(
        self, model: str, limit_tokens: int = None, limit_requests: int = None
    ):
        model_obj = PerplexityModel(
            model=model,
            api_key=self.api_key,
            endpoint="chat/completions",
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
        return ["user", "assistant", "system"]

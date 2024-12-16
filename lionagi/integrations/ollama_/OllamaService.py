# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect

from lionagi.service import Service, register_service

from .api_endpoints.api_request import OllamaRequest
from .api_endpoints.match_data_model import match_data_model
from .OllamaModel import OllamaModel


@register_service
class OllamaService(Service):
    def __init__(
        self,
        name: str = None,
    ):
        self.name = name
        self.rate_limiters = {}  # model: RateLimiter

    def check_rate_limiter(
        self,
        ollama_model: OllamaModel,
        limit_requests: int = None,
        limit_tokens: int = None,
    ):
        model = ollama_model.model

        if model not in self.rate_limiters:
            self.rate_limiters[model] = ollama_model.rate_limiter
        else:
            ollama_model.rate_limiter = self.rate_limiters[model]
            if limit_requests:
                ollama_model.rate_limiter.limit_requests = limit_requests
            if limit_tokens:
                ollama_model.rate_limiter.limit_tokens = limit_tokens

        return ollama_model

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
                "check_rate_limiter",
                "match_data_model",
            ]:
                methods.append(name)
        return methods

    # Generate a completion
    def generate_completion(
        self, model: str, limit_tokens: int = None, limit_requests: int = None
    ):
        model_obj = OllamaModel(
            model=model,
            endpoint="generate",
            method="POST",
            limit_tokens=limit_tokens,
            limit_requests=limit_requests,
        )

        return self.check_rate_limiter(
            model_obj, limit_requests=limit_requests, limit_tokens=limit_tokens
        )

    # Generate a chat completion
    def generate_chat_completion(
        self, model: str, limit_tokens: int = None, limit_requests: int = None
    ):
        model_obj = OllamaModel(
            model=model,
            endpoint="chat",
            method="POST",
            limit_tokens=limit_tokens,
            limit_requests=limit_requests,
        )

        return self.check_rate_limiter(
            model_obj, limit_requests=limit_requests, limit_tokens=limit_tokens
        )

    # Generate Embeddings
    def generate_embeddings(
        self, model: str, limit_tokens: int = None, limit_requests: int = None
    ):
        model_obj = OllamaModel(
            model=model,
            endpoint="embed",
            method="POST",
            limit_tokens=limit_tokens,
            limit_requests=limit_requests,
        )

        return self.check_rate_limiter(
            model_obj, limit_requests=limit_requests, limit_tokens=limit_tokens
        )

    # Create a Model
    def create_model(self):
        return OllamaRequest(endpoint="create", method="POST")

    # List Local Models
    def list_local_models(self):
        return OllamaRequest(endpoint="tags", method="GET")

    # Show Model Information
    def show_model_information(self):
        return OllamaRequest(endpoint="show", method="POST")

    # Copy a Model
    def copy_model(self):
        return OllamaRequest(endpoint="copy", method="POST")

    # Delete a Model
    def delete_model(self):
        return OllamaRequest(endpoint="delete", method="DELETE")

    # Pull a Model
    def pull_model(self):
        return OllamaRequest(endpoint="pull", method="POST")

    # Push a Model
    def push_model(self):
        return OllamaRequest(endpoint="push", method="POST")

    # List Running Models
    def list_running_models(self):
        return OllamaRequest(endpoint="ps", method="GET")

    @property
    def allowed_roles(self):
        return ["user", "assistant", "system"]

# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import warnings
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    model_validator,
)

from lionagi.service.rate_limiter import RateLimiter, RateLimitError
from lionagi.service.service_util import invoke_retry
from lionagi.service.token_calculator import TiktokenCalculator

from .api_endpoints.data_models import (
    GroqChatCompletionRequest,
    GroqEndpointRequestBody,
)
from .api_endpoints.groq_request import GroqRequest
from .api_endpoints.response_utils import match_response

load_dotenv()
path = Path(__file__).parent

price_config_file_name = path / "groq_price_data.yaml"
max_output_token_file_name = path / "groq_max_output_token_data.yaml"
rate_limits_file_name = path / "groq_rate_limits.yaml"


class GroqModel(BaseModel):
    model: str = Field(description="ID of the model to use.")
    request_model: GroqRequest = Field(description="Making requests")
    rate_limiter: RateLimiter | None = Field(
        default=None, description="Rate Limiter to track usage"
    )
    text_token_calculator: TiktokenCalculator | None = Field(
        default=None, description="Token Calculator"
    )
    estimated_output_len: int = Field(
        default=0, description="Expected output len before making request"
    )

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def parse_input(cls, data: dict):
        if not isinstance(data, dict):
            raise ValueError("Invalid init param")

        # Parse request model
        request_model_params = {
            "api_key": data.pop("api_key", None),
            "endpoint": data.pop("endpoint", None),
            "method": data.pop("method", None),
            "content_type": data.pop("content_type", None),
        }
        data["request_model"] = GroqRequest(**request_model_params)

        # Load rate limits from YAML
        try:
            with open(rate_limits_file_name) as file:
                rate_limits = yaml.safe_load(file)
                model_name = data.get("model")
                model_limits = None

                if model_name in rate_limits.get("text_models", {}):
                    model_limits = rate_limits["text_models"][model_name]
                elif model_name in rate_limits.get("audio_models", {}):
                    model_limits = rate_limits["audio_models"][model_name]

                if model_limits:
                    rate_limiter_params = {}
                    if limit_tokens := data.pop("limit_tokens", None):
                        rate_limiter_params["limit_tokens"] = limit_tokens
                    elif "tokens_per_minute" in model_limits:
                        rate_limiter_params["limit_tokens"] = model_limits[
                            "tokens_per_minute"
                        ]

                    if limit_requests := data.pop("limit_requests", None):
                        rate_limiter_params["limit_requests"] = limit_requests
                    elif "requests_per_minute" in model_limits:
                        rate_limiter_params["limit_requests"] = model_limits[
                            "requests_per_minute"
                        ]

                    if rate_limiter_params:
                        data["rate_limiter"] = RateLimiter(
                            **rate_limiter_params
                        )
        except FileNotFoundError:
            warnings.warn(
                f"Rate limits file not found: {rate_limits_file_name}"
            )

        # Initialize token calculator
        try:
            text_calc = TiktokenCalculator(encoding_name="cl100k_base")
            data["text_token_calculator"] = text_calc
        except Exception as e:
            warnings.warn(f"Failed to initialize token calculator: {str(e)}")

        return data

    @field_serializer("request_model")
    def serialize_request_model(self, value: GroqRequest):
        return value.model_dump(exclude_unset=True)

    @invoke_retry(max_retries=3, base_delay=1, max_delay=60)
    async def invoke(self, **kwargs):
        """Make a request to the Groq API."""
        # Extract request body from kwargs
        request_body = kwargs.get("request_body")
        if not request_body:
            raise ValueError("request_body is required")

        # Extract other parameters
        estimated_output_len = kwargs.get("estimated_output_len", 0)
        output_file = kwargs.get("output_file")
        parse_response = kwargs.get("parse_response", True)

        if request_model := getattr(request_body, "model", None):
            if request_model != self.model:
                raise ValueError(
                    f"Request model does not match. Model is {self.model}, but request is made for {request_model}."
                )

        # Check rate limits if enabled
        if self.rate_limiter:
            input_token_len = await self.get_input_token_len(request_body)
            if not self.verify_invoke_viability(
                input_tokens_len=input_token_len,
                estimated_output_len=estimated_output_len,
            ):
                raise RateLimitError("Rate limit reached")

        try:
            if getattr(request_body, "stream", False):
                return await self.stream(
                    request_body=request_body,
                    output_file=output_file,
                    parse_response=parse_response,
                )

            response_body, response_headers = await self.request_model.invoke(
                request_body=request_body,
                output_file=output_file,
                with_response_header=True,
                parse_response=False,
            )

            if response_body:
                # Update rate limits based on usage
                if self.rate_limiter:
                    if usage := response_body.get("usage"):
                        total_tokens = usage.get("total_tokens", 0)
                        self.rate_limiter.update_rate_limit(
                            response_headers.get("Date"), total_tokens
                        )
                    else:
                        self.rate_limiter.update_rate_limit(
                            response_headers.get("Date")
                        )

            if parse_response:
                return match_response(self.request_model, response_body)
            return response_body

        except Exception as e:
            raise e

    async def stream(
        self,
        request_body: GroqEndpointRequestBody,
        output_file: str | None = None,
        parse_response: bool = True,
    ):
        """Stream response from the Groq API."""
        response_chunks = []
        response_headers = None

        async for chunk in self.request_model.stream(
            request_body=request_body,
            output_file=output_file,
            with_response_header=True,
        ):
            if isinstance(chunk, dict):
                if "choices" in chunk or "usage" in chunk:
                    response_chunks.append(chunk)
                elif "headers" in chunk:
                    response_headers = chunk["headers"]

        # Update rate limits if usage information is available
        if self.rate_limiter and response_chunks:
            last_chunk = response_chunks[-1]
            if usage := last_chunk.get("usage"):
                total_tokens = usage.get("total_tokens", 0)
                if response_headers:
                    self.rate_limiter.update_rate_limit(
                        response_headers.get("Date"), total_tokens
                    )

        if parse_response:
            return match_response(self.request_model, response_chunks)
        return response_chunks

    async def get_input_token_len(
        self, request_body: GroqEndpointRequestBody | dict
    ) -> int:
        """Calculate the number of input tokens."""
        if not isinstance(request_body, (GroqEndpointRequestBody, dict)):
            return 0

        if isinstance(request_body, dict):
            request_body = GroqChatCompletionRequest(**request_body)

        if not self.text_token_calculator:
            warnings.warn(
                "Token calculator not available, using approximate token count"
            )
            # Approximate token count (1 token ≈ 4 characters)
            if isinstance(request_body, GroqChatCompletionRequest):
                messages_text = "\n".join(
                    msg.content for msg in request_body.messages
                )
                return len(messages_text) // 4
            return 0

        total_tokens = 0
        if isinstance(request_body, GroqChatCompletionRequest):
            for message in request_body.messages:
                total_tokens += self.text_token_calculator.calculate(
                    message.content
                )

        return total_tokens

    def verify_invoke_viability(
        self, input_tokens_len: int = 0, estimated_output_len: int = 0
    ) -> bool:
        """Check if the request can be made within rate limits."""
        if not self.rate_limiter:
            return True

        self.rate_limiter.release_tokens()

        estimated_output_len = (
            estimated_output_len
            if estimated_output_len != 0
            else self.estimated_output_len
        )

        if estimated_output_len == 0:
            try:
                with open(max_output_token_file_name) as file:
                    output_token_config = yaml.safe_load(file)
                    estimated_output_len = output_token_config.get(
                        self.model, 2048
                    )  # Default to 2048
                    self.estimated_output_len = estimated_output_len
            except FileNotFoundError:
                warnings.warn(
                    f"Max output token file not found: {max_output_token_file_name}"
                )
                # Use a conservative default
                estimated_output_len = 2048
                self.estimated_output_len = estimated_output_len

        return self.rate_limiter.check_availability(
            input_tokens_len, estimated_output_len
        )

    def estimate_text_price(
        self,
        input_text: str,
        estimated_num_of_output_tokens: int = 0,
    ) -> float:
        """Estimate the cost of processing text."""
        if not self.text_token_calculator:
            warnings.warn(
                "Token calculator not available, using approximate token count"
            )
            # Approximate token count (1 token ≈ 4 characters)
            num_of_input_tokens = len(input_text) // 4
        else:
            num_of_input_tokens = self.text_token_calculator.calculate(
                input_text
            )

        try:
            with open(price_config_file_name) as file:
                price_config = yaml.safe_load(file)
        except FileNotFoundError:
            raise ValueError(
                f"Price config file not found: {price_config_file_name}"
            )

        if self.model not in price_config.get("model", {}):
            raise ValueError(
                f"No price information found for model: {self.model}"
            )

        model_price_info = price_config["model"][self.model]
        estimated_price = (
            model_price_info["input_tokens"] * num_of_input_tokens
            + model_price_info["output_tokens"]
            * estimated_num_of_output_tokens
        )

        return estimated_price

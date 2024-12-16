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

from .api_endpoints.api_request import OpenAIRequest
from .api_endpoints.chat_completions.request.request_body import (
    OpenAIChatCompletionRequestBody,
    StreamOptions,
)
from .api_endpoints.chat_completions.util import get_images, get_text_messages
from .api_endpoints.data_models import OpenAIEndpointRequestBody
from .api_endpoints.embeddings.request_body import OpenAIEmbeddingRequestBody
from .api_endpoints.match_response import match_response
from .image_token_calculator.image_token_calculator import (
    OpenAIImageTokenCalculator,
)

load_dotenv()
path = Path(__file__).parent

price_config_file_name = path / "openai_max_output_token_data.yaml"
max_output_token_file_name = path / "openai_price_data.yaml"


class OpenAIModel(BaseModel):
    model: str = Field(description="ID of the model to use.")

    request_model: OpenAIRequest = Field(description="Making requests")

    rate_limiter: RateLimiter = Field(
        description="Rate Limiter to track usage"
    )

    text_token_calculator: TiktokenCalculator = Field(
        default=None, description="Token Calculator"
    )

    image_token_calculator: OpenAIImageTokenCalculator = Field(
        default=None, description="Image Token Calculator"
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

        # parse request model
        request_model_params = {
            "api_key": data.pop("api_key", None),
            "endpoint": data.pop("endpoint", None),
            "method": data.pop("method", None),
        }
        if org := data.pop("openai_organization", None):
            request_model_params["openai_organization"] = org
        if proj := data.pop("openai_project", None):
            request_model_params["openai_project"] = proj
        if content_type := data.pop("content_type", None):
            request_model_params["content_type"] = content_type

        data["request_model"] = OpenAIRequest(**request_model_params)

        # parse rate limiter
        if "rate_limiter" not in data:
            rate_limiter_params = {}
            if limit_tokens := data.pop("limit_tokens", None):
                rate_limiter_params["limit_tokens"] = limit_tokens
            if limit_requests := data.pop("limit_requests", None):
                rate_limiter_params["limit_requests"] = limit_requests

            data["rate_limiter"] = RateLimiter(**rate_limiter_params)

        # parse token calculator
        try:
            text_calc = TiktokenCalculator(encoding_name=data.get("model"))
            data["text_token_calculator"] = text_calc
        except Exception:
            pass

        # set image calcultor
        try:
            data["image_token_calculator"] = OpenAIImageTokenCalculator(
                model=data.get("model")
            )
        except Exception:
            pass

        return data

    @field_serializer("request_model")
    def serialize_request_model(self, value: OpenAIRequest):
        return value.model_dump(exclude_unset=True)

    @invoke_retry(max_retries=3, base_delay=1, max_delay=60)
    async def invoke(
        self,
        request_body: OpenAIEndpointRequestBody,
        estimated_output_len: int = 0,
        output_file=None,
        parse_response=True,
    ):
        if request_model := getattr(request_body, "model"):
            if request_model != self.model:
                raise ValueError(
                    f"Request model does not match. Model is {self.model}, but request is made for {request_model}."
                )

        if getattr(request_body, "stream", None) and not isinstance(
            request_body, OpenAIChatCompletionRequestBody
        ):
            raise ValueError("Stream is only supported for chat completions")

        # check remaining rate limit
        input_token_len = await self.get_input_token_len(request_body)

        # chat completion request body attribute
        if getattr(request_body, "max_completion_tokens", None):
            estimated_output_len = request_body.max_completion_tokens

        invoke_viability_result = self.verify_invoke_viability(
            input_tokens_len=input_token_len,
            estimated_output_len=estimated_output_len,
        )
        if not invoke_viability_result:
            raise RateLimitError("Rate limit reached for requests")

        try:
            if getattr(request_body, "stream", None):
                return await self.stream(
                    request_body,
                    output_file=output_file,
                    parse_response=parse_response,
                )

            if getattr(request_body, "file", None):
                response_body, response_headers = (
                    await self.request_model.invoke(
                        form_data=request_body,
                        output_file=output_file,
                        with_response_header=True,
                        parse_response=False,
                    )
                )
            else:
                response_body, response_headers = (
                    await self.request_model.invoke(
                        json_data=request_body,
                        output_file=output_file,
                        with_response_header=True,
                        parse_response=False,
                    )
                )

            self.check_limits_info(response_headers)

            if response_body:
                # mainly for chat/completions and embedding endpoints
                # update rate limit
                if response_body.get("usage"):
                    total_token_usage = response_body["usage"]["total_tokens"]
                    self.rate_limiter.update_rate_limit(
                        response_headers.get("Date"), total_token_usage
                    )
                else:  # No Token limits condition (request limit only)
                    self.rate_limiter.update_rate_limit(
                        response_headers.get("Date")
                    )
            else:
                # for audio/speech endpoint (without response body object)
                self.rate_limiter.update_rate_limit(
                    response_headers.get("Date")
                )

            self.check_remaining_info(response_headers)

            if parse_response:
                return match_response(self.request_model, response_body)
            else:
                return response_body

        except Exception as e:  # TODO: example
            raise e

    async def stream(
        self,
        request_body: OpenAIEndpointRequestBody,
        output_file=None,
        parse_response=True,
    ):
        if not isinstance(request_body, OpenAIChatCompletionRequestBody):
            raise ValueError("Stream is only supported for chat completions")

        stream_options_included = bool(getattr(request_body, "stream_options"))
        if not stream_options_included:
            setattr(
                request_body,
                "stream_options",
                StreamOptions(include_usage=True),
            )

        response_list = []
        async for chunk in self.request_model.stream(
            json_data=request_body,
            output_file=output_file,
            with_response_header=True,
        ):
            response_list.append(chunk)

        response_headers = response_list.pop()
        if stream_options_included:
            usage_chunk = response_list[-1]
        else:
            usage_chunk = response_list.pop()

        self.check_limits_info(response_headers)
        total_token_usage = usage_chunk["usage"]["total_tokens"]
        self.rate_limiter.update_rate_limit(
            response_headers.get("Date"), total_token_usage
        )

        if parse_response:
            return match_response(self.request_model, response_list)
        else:
            return response_list

    async def get_input_token_len(
        self, request_body: OpenAIEndpointRequestBody
    ):
        if request_model := getattr(request_body, "model"):
            if request_model != self.model:
                raise ValueError(
                    f"Request model does not match. Model is {self.model}, but request is made for {request_model}."
                )
        # TODO: match with new Request Body format
        if isinstance(request_body, OpenAIChatCompletionRequestBody):
            messages_text = get_text_messages(request_body)
            # text_token_calculator should always be available for chat completions
            text_tokens = self.text_token_calculator.calculate(messages_text)

            image_urls = get_images(request_body)
            image_tokens = 0
            for url, detail in image_urls:
                if self.image_token_calculator:
                    image_tokens += (
                        await self.image_token_calculator.calculate(
                            url, detail
                        )
                    )
                else:
                    raise ValueError(
                        "The model does not have vision capabilities."
                    )

            return text_tokens + image_tokens
        elif isinstance(request_body, OpenAIEmbeddingRequestBody):
            text = request_body.input
            if isinstance(text, str):  # str
                return self.text_token_calculator.calculate(text)
            elif isinstance(text[0], int):  # List[int]
                return len(text)
            elif isinstance(text[0], str):  # List[str]
                total_totkens = 0
                for t in text:
                    total_totkens += self.text_token_calculator.calculate(t)
                return total_totkens
            else:  # List[List[int]]
                total_tokens = 0
                for t in text:
                    total_tokens += len(t)
                return total_tokens

        # TODO: add other rules for other endpoints if input tokens should be calculated
        return 0  # no tokens rate limit

    def verify_invoke_viability(
        self, input_tokens_len: int = 0, estimated_output_len: int = 0
    ):
        self.rate_limiter.release_tokens()

        estimated_output_len = (
            estimated_output_len
            if estimated_output_len != 0
            else self.estimated_output_len
        )
        if estimated_output_len == 0:
            with open(max_output_token_file_name) as file:
                output_token_config = yaml.safe_load(file)
                estimated_output_len = output_token_config.get(self.model, 0)
                self.estimated_output_len = (
                    estimated_output_len  # update to default max output len
                )

        if self.rate_limiter.check_availability(
            input_tokens_len, estimated_output_len
        ):
            return True
        else:
            return False

    def check_limits_info(self, response_headers):
        if response_headers.get("x-ratelimit-limit-requests"):
            if self.rate_limiter.limit_requests is None:
                self.rate_limiter.limit_requests = int(
                    response_headers.get("x-ratelimit-limit-requests")
                )
            else:
                if self.rate_limiter.limit_requests > int(
                    response_headers.get("x-ratelimit-limit-requests")
                ):
                    warnings.warn(
                        "The configured request limit exceeds the account's allowed request limit."
                        "This may lead to unexpected throttling or rejection of requests.",
                        UserWarning,
                    )
        if response_headers.get("x-ratelimit-limit-tokens"):
            if self.rate_limiter.limit_tokens is None:
                self.rate_limiter.limit_tokens = int(
                    response_headers.get("x-ratelimit-limit-tokens")
                )
            else:
                if self.rate_limiter.limit_tokens > int(
                    response_headers.get("x-ratelimit-limit-tokens")
                ):
                    warnings.warn(
                        "The configured token limit exceeds the account's allowed token limit."
                        "This may lead to unexpected throttling or rejection of requests.",
                        UserWarning,
                    )

    def check_remaining_info(self, response_headers):
        if response_headers.get("x-ratelimit-remaining-tokens"):
            if (
                int(response_headers.get("x-ratelimit-remaining-tokens"))
                < self.rate_limiter.remaining_tokens
            ):
                token_diff = self.rate_limiter.remaining_tokens - int(
                    response_headers.get("x-ratelimit-remaining-tokens")
                )
                self.rate_limiter.update_rate_limit(
                    response_headers.get("Date"), token_diff
                )

        if response_headers.get("x-ratelimit-remaining-requests"):
            if (
                int(response_headers.get("x-ratelimit-remaining-requests"))
                < self.rate_limiter.remaining_requests
            ):
                request_diff = self.rate_limiter.remaining_requests - int(
                    response_headers.get("x-ratelimit-remaining-requests")
                )
                for i in range(request_diff):
                    self.rate_limiter.update_rate_limit(
                        response_headers.get("Date")
                    )

    def estimate_text_price(
        self,
        input_text: str,
        with_batch: bool = False,
        estimated_num_of_output_tokens: int = 0,
    ):
        if self.text_token_calculator is None:
            raise ValueError(
                "Estimating price currently only supports chat/completions endpoint"
            )

        # only if text_token_calculator is available
        num_of_input_tokens = self.text_token_calculator.calculate(input_text)

        # read openai price info from config file
        with open(price_config_file_name) as file:
            price_config = yaml.safe_load(file)

        if self.request_model.endpoint == "chat/completions":
            model_price_info_dict = price_config["model"][self.model]
            if with_batch:
                estimated_price = (
                    model_price_info_dict["input_tokens_with_batch"]
                    * num_of_input_tokens
                    + model_price_info_dict["output_tokens_with_batch"]
                    * estimated_num_of_output_tokens
                )
            else:
                estimated_price = (
                    model_price_info_dict["input_tokens"] * num_of_input_tokens
                    + model_price_info_dict["output_tokens"]
                    * estimated_num_of_output_tokens
                )

        else:
            # TODO: add price config for other endpoints
            raise ValueError(
                "Estimating price currently only supports chat/completions endpoint"
            )
        return estimated_price

    @property
    def allowed_roles(self):
        return ["user", "assistant", "system"]

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
    field_serializer,
)

from openai_service.OpenAIEndpointRequestBody import (
    OpenAIEndpointRequestBody,
    OpenAIChatCompletionsRequestBody,
)
from openai_service.OpenAIRequestModel import OpenAIRequest
from openai_service.RateLimiter import RateLimiter
from openai_service.TokenCalculator import TiktokenCalculator

from dotenv import load_dotenv

load_dotenv()

price_config_file_name = "Test_openai_price_data.yaml"


class OpenAIModel(BaseModel):
    model: str = Field(description="ID of the model to use.")

    request_model: OpenAIRequest = Field(description="Making requests")

    rate_limiter: RateLimiter = Field(description="Rate Limiter to track usage")

    text_token_calculator: TiktokenCalculator = Field(
        default=None, description="Token Calculator"
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
        rate_limiter_params = {
            "limit_tokens": data.pop("limit_tokens", None),
            "limit_requests": data.pop("limit_requests", None),
        }

        data["rate_limiter"] = RateLimiter(**rate_limiter_params)

        # parse token calculator
        try:
            text_calc = TiktokenCalculator(encoding_name=data.get("model"))
            data["text_token_calculator"] = text_calc
        except:
            pass

        return data

    @field_serializer("request_model")
    def serialize_request_model(self, value: OpenAIRequest):
        return value.model_dump(exclude_unset=True)

    async def invoke(self, request_body: OpenAIEndpointRequestBody = None):
        if request_model := getattr(request_body, "model"):
            if request_model != self.model:
                raise ValueError("Request model does not match.")

        if self.rate_limiter:
            self.rate_limiter.release_tokens()
        # TODO: check remaining tokens and requests before making request

        try:
            response_body, response_headers = await self.request_model.invoke(
                request_body
            )

            # TODO: for rate limiter check
            account_limit_request = response_headers.get("x-ratelimit-limit-requests")
            account_limit_tokens = response_headers.get("x-ratelimit-limit-tokens")
            account_remaining_requests = response_headers.get(
                "x-ratelimit-remaining-requests"
            )
            account_remaining_tokens = response_headers.get(
                "x-ratelimit-remaining-tokens"
            )

            # mainly for chat/completions and embedding endpoints
            # update rate limit
            if response_body.get("usage"):
                self.rate_limiter.update_text_rate_limit(response_body, response_headers)

            return response_body

        except Exception as e:  # TODO: example
            return e

    def estimate_price(
        self,
        input_text: str,
        with_batch: bool = False,
        estimated_num_of_output_tokens: int = 0,
    ):
        import yaml
        # only if text_token_calculator is available
        num_of_input_tokens = self.text_token_calculator.calculate(input_text)

        # read openai price info from config file
        with open(price_config_file_name, "r") as file:
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


OAI_REQUEST_BODY = {"chat/completions": OpenAIChatCompletionsRequestBody}


async def main():
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ]

    model = "gpt-4o-mini"

    obj = OpenAIChatCompletionsRequestBody(model=model, messages=messages)

    output = obj.model_dump(exclude_unset=True)

    print("\nDATA:")
    print(output)

    # objr = OpenAIRequest(
    #     api_key="OPENAI_API_KEY",
    #     endpoint="chat/completions",
    #     method="POST",
    #     content_type="application/json",
    # )
    #
    # print("\nREQUEST:")
    # print(objr.model_dump(exclude_unset=True))

    oo = OpenAIModel(
        model="gpt-4o-mini",
        api_key="OPENAI_API_KEY",
        endpoint="chat/completions",
        method="POST",
        limit_tokens=10000,
        limit_requests=10000,
    )
    response = await oo.invoke(request_body=obj)

    print("\nRESPONSE:")
    print(response)

    print(oo.rate_limiter.remaining_requests)
    print(oo.rate_limiter.remaining_tokens)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
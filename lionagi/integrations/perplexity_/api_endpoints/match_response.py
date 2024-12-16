from typing import Any, Dict, List, Union

from lionagi.integrations.perplexity_.api_endpoints.api_request import (
    PerplexityRequest,
)
from lionagi.integrations.perplexity_.api_endpoints.chat_completions.response.response_body import (
    PerplexityChatCompletionResponseBody,
)


def match_response(
    request_model: PerplexityRequest,
    response_body: dict[str, Any] | list[dict[str, Any]],
) -> PerplexityChatCompletionResponseBody | list[dict[str, Any]]:
    """Match the response body to the appropriate response model based on the endpoint."""

    if not response_body:
        return response_body

    if isinstance(response_body, list):
        return response_body

    if request_model.endpoint == "chat/completions":
        return PerplexityChatCompletionResponseBody(**response_body)

    return response_body

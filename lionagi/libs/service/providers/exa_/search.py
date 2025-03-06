from typing import Literal

from lionagi.service.endpoints.base import EndPoint

from .models import ExaSearchRequest

CATEGORY_OPTIONS = Literal[
    "article",
    "book",
    "company",
    "research paper",
    "news",
    "pdf",
    "github",
    "tweet",
    "personal site",
    "linkedin profile",
    "financial report",
]

SEARCH_CONFIG = {
    "name": "search_exa",
    "provider": "exa",
    "base_url": "https://api.exa.ai",
    "endpoint": "search",
    "method": "post",
    "openai_compatible": False,
    "is_invokeable": False,
    "requires_tokens": False,
    "is_streamable": False,
    "required_kwargs": {
        "query",
    },
    "optional_kwargs": {
        "category",
        "contents",
        "endCrawlDate",
        "endPublishedDate",
        "excludeDomains",
        "excludeText",
        "includeDomains",
        "includeText",
        "numResults",
        "startCrawlDate",
        "startPublishedDate",
        "type",  # keyword, neural, auto
        "useAutoPrompt",
    },
    "request_options": ExaSearchRequest,
}


class ExaSearchEndPoint(EndPoint):

    def __init__(self, config: dict = SEARCH_CONFIG):
        super().__init__(config)

    def create_payload(
        self, request_obj: "ExaSearchRequest" = None, **kwargs
    ) -> dict:
        if request_obj is not None:
            kwargs.update(request_obj.to_dict(exclude_none=True))

        payload = {}
        is_cached = kwargs.get("is_cached", False)
        headers = kwargs.get("headers", {})

        for k, v in kwargs.items():
            if k in self.acceptable_kwargs:
                payload[k] = v
        if "api_key" in kwargs:
            headers["x-api-key"] = kwargs["api_key"]
        if "content-type" not in kwargs:
            headers["content-type"] = "application/json"

        return {
            "payload": payload,
            "headers": headers,
            "is_cached": is_cached,
        }

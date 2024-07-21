import re

CAHCED_CONFIG = {
    "ttl": 300,
    "key": None,
    "namespace": None,
    "key_builder": None,
    "skip_cache_func": lambda x: False,
    "serializer": None,
    "plugins": None,
    "alias": None,
    "noself": False,
}

TOKEN_LIMIT_CONFIG = {
    "token_encoding_name": None,
    "max_requests": 10000,
    "max_tokens": 1000000,
    "interval": 60,
}


def api_endpoint_from_url(request_url: str) -> str:
    match = re.search(r"^https://[^/]+(/.+)?/v\d+/(.+)$", request_url)
    return match[2] if match else ""

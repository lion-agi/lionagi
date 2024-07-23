from typing import Any
import re


def api_endpoint_from_url(request_url: str) -> str:
    match = re.search(r"^https://[^/]+(/.+)?/v\d+/(.+)$", request_url)
    return match[2] if match else ""


def create_payload(
    input_: Any,
    config: dict,
    required_: list | tuple,
    optional_: list | tuple,
    input_key: str,
    **kwargs,
):
    config = {**config, **kwargs}
    payload = {input_key: input_}

    for key in required_:
        payload[key] = config[key]

    for key in optional_:
        if bool(config[key]) and str(config[key]).strip().lower() != "none":
            payload[key] = config[key]

    return payload

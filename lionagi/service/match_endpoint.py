from .endpoint import EndPoint


def match_endpoint(
    provider: str,
    base_url: str,
    endpoint: str,
    endpoint_params: list[str] | None = None,
) -> EndPoint: ...

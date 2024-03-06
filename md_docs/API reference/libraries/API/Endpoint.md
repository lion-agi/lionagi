```
from lionagi.libs.ln_api import EndPoint
```

# EndPoint

The `EndPoint` class represents an API endpoint with rate limiting capabilities. It encapsulates the details of an API endpoint, including its [[Rate Limiter]].

## Attributes

- `endpoint`: The API endpoint path.
- `rate_limiter_class`: The class used for rate limiting requests to the endpoint.
- `max_requests`: The maximum number of requests allowed per interval.
- `max_tokens`: The maximum number of tokens allowed per interval.
- `interval`: The time interval in seconds for replenishing rate limit capacities.
- `config`: Configuration parameters for the endpoint.
- `rate_limiter`: The rate limiter instance for this endpoint.

## Methods

### `__init__(max_requests: int = 1000, max_tokens: int = 100000, interval: int = 60, endpoint_: str | None = None, rate_limiter_class: Type[BaseRateLimiter] = SimpleRateLimiter, token_encoding_name=None, config: Mapping = None) -> None`

Initializes the `EndPoint` with the specified parameters.

- `max_requests`: The maximum number of requests allowed per interval (default is 1000).
- `max_tokens`: The maximum number of tokens allowed per interval (default is 100000).
- `interval`: The time interval in seconds for replenishing rate limit capacities (default is 60).
- `endpoint_`: The API endpoint path.
- `rate_limiter_class`: The class used for rate limiting requests to the endpoint (default is `SimpleRateLimiter`).
- `token_encoding_name`: The name of the token encoding to use.
- `config`: Configuration parameters for the endpoint.

### `init_rate_limiter() -> None`

Initializes the rate limiter for the endpoint.

Examples:
```python
endpoint = EndPoint(
    max_requests=100,
    max_tokens=1000,
    interval=60,
    endpoint_='chat/completions',
    rate_limiter_class=SimpleRateLimiter,
    config={'param1': 'value1'}
)
await endpoint.init_rate_limiter()

while True:
    if await endpoint.rate_limiter.request_permission(10):
        # Make the API call
        response = await endpoint.rate_limiter._call_api(http_session, endpoint.endpoint, base_url, api_key)
        # Process the response
    else:
        # Wait and retry later
        await asyncio.sleep(1)
```


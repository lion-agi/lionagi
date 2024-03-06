```
from lionagi.libs.ln_api import SimpleRateLimiter
```

# BaseRateLimiter

The `BaseRateLimiter` class is an abstract base class for implementing rate limiters. It provides the basic structure for rate limiters, including the replenishment of request and token capacities at regular intervals.

## Attributes

- `interval`: The time interval in seconds for replenishing capacities.
- `max_requests`: The maximum number of requests allowed per interval.
- `max_tokens`: The maximum number of tokens allowed per interval.
- `available_request_capacity`: The current available request capacity.
- `available_token_capacity`: The current available token capacity.
- `rate_limit_replenisher_task`: The asyncio task for replenishing capacities.

## Methods

### `__init__(max_requests: int, max_tokens: int, interval: int = 60, token_encoding_name=None) -> None`

Initializes the `BaseRateLimiter` with the specified parameters.

- `max_requests`: The maximum number of requests allowed per interval.
- `max_tokens`: The maximum number of tokens allowed per interval.
- `interval`: The time interval in seconds for replenishing capacities (default is 60).
- `token_encoding_name`: The name of the token encoding to use.

### `start_replenishing() -> NoReturn`

Starts the replenishment of rate limit capacities at regular intervals.

### `stop_replenishing() -> None`

Stops the replenishment task.

### `request_permission(required_tokens) -> bool`

Requests permission to make an API call. Returns `True` if the request can be made immediately, otherwise `False`.

### `create(max_requests: int, max_tokens: int, interval: int = 60, token_encoding_name=None) -> "BaseRateLimiter"`

Creates an instance of `BaseRateLimiter` and starts the replenisher task.

- `max_requests`: The maximum number of requests allowed per interval.
- `max_tokens`: The maximum number of tokens allowed per interval.
- `interval`: The time interval in seconds for replenishing capacities (default is 60).
- `token_encoding_name`: The name of the token encoding to use.

Returns an instance of `BaseRateLimiter` with the replenisher task started.

Examples:
```python
rate_limiter = await BaseRateLimiter.create(100, 1000, 60)
while True:
    if await rate_limiter.request_permission(10):
        # Make the API call
        response = await rate_limiter._call_api(http_session, endpoint, base_url, api_key)
        # Process the response
    else:
        # Wait and retry later
        await asyncio.sleep(1)
```

# SimpleRateLimiter

The `SimpleRateLimiter` class is a simple implementation of a rate limiter. It inherits from `BaseRateLimiter` and provides a basic rate limiting mechanism.

## Methods

### `__init__(max_requests: int, max_tokens: int, interval: int = 60, token_encoding_name=None) -> None`

Initializes the `SimpleRateLimiter` with the specified parameters.

- `max_requests`: The maximum number of requests allowed per interval.
- `max_tokens`: The maximum number of tokens allowed per interval.
- `interval`: The time interval in seconds for replenishing capacities (default is 60).
- `token_encoding_name`: The name of the token encoding to use.

Examples:
```python
rate_limiter = SimpleRateLimiter(100, 1000, 60)
await rate_limiter.start_replenishing()
while True:
    if await rate_limiter.request_permission(10):
        # Make the API call
        response = await rate_limiter._call_api(http_session, endpoint, base_url, api_key)
        # Process the response
    else:
        # Wait and retry later
        await asyncio.sleep(1)
```

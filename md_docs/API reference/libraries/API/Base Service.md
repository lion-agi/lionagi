```
from lionagi.libs.ln_api import BaseService
```
# BaseService

The `BaseService` class is a base class for services that interact with API endpoints. It provides a foundation for services that need to make API calls with [[Rate Limiter|rate limiting]].

## Attributes

- `api_key`: The API key used for authentication.
- `schema`: The schema defining the service's endpoints.
- `status_tracker`: The object tracking the status of API calls.
- `endpoints`: A dictionary of [[Endpoint]] objects.

## Methods

### `__init__(api_key: str | None = None, schema: Mapping[str, Any] = None, token_encoding_name: str = None, max_tokens: int = 100_000, max_requests: int = 1_000, interval: int = 60) -> None`

Initializes the `BaseService` with the specified parameters.

- `api_key`: The API key used for authentication.
- `schema`: The schema defining the service's endpoints.
- `token_encoding_name`: The name of the token encoding to use.
- `max_tokens`: The maximum number of tokens allowed per interval (default is 100,000).
- `max_requests`: The maximum number of requests allowed per interval (default is 1,000).
- `interval`: The time interval in seconds for replenishing rate limit capacities (default is 60).

### `init_endpoint(endpoint_: Sequence | str | EndPoint | None = None) -> None`

Initializes the specified endpoint or all endpoints if none is specified.

- `endpoint_`: The endpoint(s) to initialize. Can be a string, an `EndPoint`, a list of strings, or a list of `EndPoint`s.

Examples:
```python
service = BaseService(api_key='your_api_key', schema=your_schema)
await service.init_endpoint('chat/completions')
await service.init_endpoint(['chat/completions', 'embeddings'])

endpoint = EndPoint(max_requests=100, max_tokens=1000, interval=60, endpoint_='custom/endpoint')
await service.init_endpoint(endpoint)
```

### `call_api(payload, endpoint, method, **kwargs)`

Calls the specified API endpoint with the given payload and method.

- `payload`: The payload to send with the API call.
- `endpoint`: The endpoint to call.
- `method`: The HTTP method to use for the call.
- `**kwargs`: Additional keyword arguments to pass to the API call.

Returns the response from the API call.

Raises a `ValueError` if the specified endpoint has not been initialized.

Examples:
```python
payload = {'format_prompt': 'Hello, how are you?'}
response = await service.call_api(payload, 'chat/completions', 'post')

payload = {'input': 'This is a sample text.'}
response = await service.call_api(payload, 'embeddings', 'post')

payload = {'custom_param': 'value'}
response = await service.call_api(payload, 'custom/endpoint', 'get', param1='value1')
```

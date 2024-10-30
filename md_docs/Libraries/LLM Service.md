## Classes:

### `StatusTracker`

^deb0a1

Keeps track of various task statuses within a system.

#### Attributes:
- `num_tasks_started` (int): The number of tasks that have been initiated.
- `num_tasks_in_progress` (int): The number of tasks currently being processed.
- `num_tasks_succeeded` (int): The number of tasks that have completed successfully.
- `num_tasks_failed` (int): The number of tasks that have failed.
- `num_rate_limit_errors` (int): The number of tasks that failed due to rate limiting.
- `num_api_errors` (int): The number of tasks that failed due to API errors.
- `num_other_errors` (int): The number of tasks that failed due to other errors.

### `BaseRateLimiter`

Abstract base class for implementing rate limiters.

#### Attributes:
- `interval` (int): The time interval in seconds for replenishing capacities.
- `max_requests` (int): The maximum number of requests allowed per interval.
- `max_tokens` (int): The maximum number of tokens allowed per interval.
- `available_request_capacity` (int): The current available request capacity.
- `available_token_capacity` (int): The current available token capacity.
- `rate_limit_replenisher_task` (AsyncUtil.Task | None): The asyncio task for replenishing capacities.

#### Methods:
- `__init__(self, max_requests: int, max_tokens: int, interval: int = 60, token_encoding_name=None) -> None`: Initializes the `BaseRateLimiter` instance.
- `async start_replenishing(self) -> NoReturn`: Starts the replenishment of rate limit capacities at regular intervals.
- `async stop_replenishing(self) -> None`: Stops the replenishment task.
- `async request_permission(self, required_tokens) -> bool`: Requests permission to make an API call. Returns True if the request can be made immediately, otherwise False.
- `async _call_api(self, http_session, endpoint: str, base_url: str, api_key: str, max_attempts: int = 3, method: str = "post", payload: Mapping[str, any] = None, **kwargs) -> Mapping[str, any] | None`: Makes an API call to the specified endpoint using the provided HTTP session.
- `classmethod async create(cls, max_requests: int, max_tokens: int, interval: int = 60, token_encoding_name=None) -> "BaseRateLimiter"`: Creates an instance of `BaseRateLimiter` and starts the replenisher task.

### `SimpleRateLimiter`

A simple implementation of a rate limiter. Inherits from `BaseRateLimiter` and provides a basic rate limiting mechanism.

#### Methods:
- `__init__(self, max_requests: int, max_tokens: int, interval: int = 60, token_encoding_name=None) -> None`: Initializes the `SimpleRateLimiter` with the specified parameters.

### `EndPoint`

Represents an API endpoint with rate limiting capabilities.

#### Attributes:
- `endpoint` (str): The API endpoint path.
- `rate_limiter_class` (Type[BaseRateLimiter]): The class used for rate limiting requests to the endpoint.
- `max_requests` (int): The maximum number of requests allowed per interval.
- `max_tokens` (int): The maximum number of tokens allowed per interval.
- `interval` (int): The time interval in seconds for replenishing rate limit capacities.
- `config` (Mapping): Configuration parameters for the endpoint.
- `rate_limiter` (Optional[BaseRateLimiter]): The rate limiter instance for this endpoint.

#### Methods:
- `__init__(self, max_requests: int = 1000, max_tokens: int = 100000, interval: int = 60, endpoint_: str | None = None, rate_limiter_class: Type[BaseRateLimiter] = SimpleRateLimiter, token_encoding_name=None, config: Mapping = None) -> None`: Initializes the `EndPoint` instance.
- `async init_rate_limiter(self) -> None`: Initializes the rate limiter for the endpoint.

### `BaseService`

^0916ce

Base class for services that interact with API endpoints.

#### Attributes:
- `api_key` (Optional[str]): The API key used for authentication.
- `schema` (Mapping[str, Any]): The schema defining the service's endpoints.
- `status_tracker` (StatusTracker): The object tracking the status of API calls.
- `endpoints` (Mapping[str, EndPoint]): A dictionary of endpoint objects.

#### Methods:
- `__init__(self, api_key: str | None = None, schema: Mapping[str, Any] = None, token_encoding_name: str = None, max_tokens: int = 100_000, max_requests: int = 1_000, interval: int = 60) -> None`: Initializes the `BaseService` instance.
- `async init_endpoint(self, endpoint_: Sequence | str | EndPoint | None = None) -> None`: Initializes the specified endpoint or all endpoints if none is specified.
- `async call_api(self, payload, endpoint, method, **kwargs)`: Calls the specified API endpoint with the given payload and method.

### `PayloadPackage`

Provides methods for creating payloads for different API operations.

#### Class Methods:
- `chat_completion(cls, messages, llmconfig, schema, **kwargs)`: Creates a payload for the chat completion operation.
- `fine_tuning(cls, training_file, llmconfig, schema, **kwargs)`: Creates a payload for the fine-tuning operation.

## Usage Example:

```python
import asyncio
from lionagi.core.rate_limit import StatusTracker, SimpleRateLimiter, EndPoint, BaseService

# Create a status tracker
tracker = StatusTracker()

# Create a rate limiter
rate_limiter = await SimpleRateLimiter.create(max_requests=100, max_tokens=1000, interval=60)

# Create an endpoint
endpoint = EndPoint(endpoint_='chat/completions', rate_limiter_class=SimpleRateLimiter)
await endpoint.init_rate_limiter()

# Create a service
service = BaseService(api_key='your_api_key')
await service.init_endpoint('chat/completions')

# Make an API call
payload = PayloadPackage.chat_completion(messages=[], llmconfig={}, schema={})
response = await service.call_api(payload, endpoint='chat/completions', method='post')
```

In this example, we demonstrate how to use the various classes provided by the module:

1. We create a `StatusTracker` instance to track task statuses.
2. We create a `SimpleRateLimiter` instance using the `create` class method, specifying the rate limit parameters.
3. We create an `EndPoint` instance for the 'chat/completions' endpoint, using the `SimpleRateLimiter` class.
4. We create a `BaseService` instance with an API key and initialize the 'chat/completions' endpoint.
5. We create a payload using the `PayloadPackage.chat_completion` method.
6. We make an API call using the `call_api` method of the service, specifying the payload, endpoint, and method.

The response from the API call can be further processed as needed.

Note: The example assumes the presence of the `lionagi.core.rate_limit` module and its dependencies.

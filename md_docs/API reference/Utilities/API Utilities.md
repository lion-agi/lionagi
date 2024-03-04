
# APIUtil Class Reference

The `APIUtil` class provides utility methods for common API interaction patterns, such as making HTTP requests, handling errors, and caching.

## Static Methods

### `api_method(http_session: aiohttp.ClientSession, method: str = "post") -> Callable`

Returns the corresponding HTTP method function from the `http_session` object.

- **Parameters:**
  - `http_session`: The session object from the `aiohttp` library.
  - `method`: The HTTP method as a string, defaulting to `"post"`.
- **Returns:** The Callable for the specified HTTP method.
- **Raises:** `ValueError` if the method is not one of the allowed ones.
- **Example:**
  ```python
  session = aiohttp.ClientSession()
  post_method = APIUtil.api_method(session, "post")
  ```

### `api_error(response_json: Dict[str, Any]) -> bool`

Checks if the given `response_json` dictionary contains an "error" key.

- **Parameters:**
  - `response_json`: The JSON response as a dictionary.
- **Returns:** `True` if there is an error, `False` otherwise.
- **Example:**
  ```python
  response_json_with_error = {"error": "Something went wrong"}
  APIUtil.api_error(response_json_with_error)  # Returns True
  ```

### `api_rate_limit_error(response_json: Dict[str, Any]) -> bool`

Checks if the error message in the `response_json` dictionary contains the phrase "Rate limit".

- **Parameters:**
  - `response_json`: The JSON response as a dictionary.
- **Returns:** `True` if the phrase "Rate limit" is found, `False` otherwise.
- **Example:**
  ```python
  response_json_with_rate_limit = {"error": {"message": "Rate limit exceeded"}}
  APIUtil.api_rate_limit_error(response_json_with_rate_limit)  # Returns True
  ```

### `api_endpoint_from_url(request_url: str) -> str`

Extracts the API endpoint from a given URL using a regular expression.

- **Parameters:**
  - `request_url`: The full URL to the API endpoint.
- **Returns:** The extracted endpoint or an empty string if the pattern does not match.
- **Example:**
  ```python
  valid_url = "https://api.example.com/v1/users"
  APIUtil.api_endpoint_from_url(valid_url)  # Returns 'users'
  ```

### `unified_api_call(http_session: aiohttp.ClientSession, method: str, url: str, **kwargs) -> Any`

Makes an API call and automatically retries on rate limit error.

- **Parameters:**
  - `http_session`: The session object from the `aiohttp` library.
  - `method`: The HTTP method as a string.
  - `url`: The URL to which the request is made.
  - `**kwargs`: Additional keyword arguments to pass to the API call.
- **Returns:** The JSON response as a dictionary.
- **Example:**
  ```python
  session = aiohttp.ClientSession()
  success_url = "https://api.example.com/v1/success"
  await APIUtil.unified_api_call(session, 'get', success_url)  # {'result': 'Success'}
  ```

### `get_cache_key(url: str, params: Optional[Dict[str, Any]]) -> str`

Creates a unique cache key based on the URL and parameters.
- **Parameters:**
  - `url`: The URL for the request.
  - `params`: The query parameters for the request.
- **Returns:** A string representing the cache key.

### `retry_api_call(http_session: aiohttp.ClientSession, url: str, retries: int = 3, backoff_factor: float = 0.5, **kwargs) -> Any`

Retries an API call on failure, with exponential backoff.

- **Parameters:**
  - `http_session`: The `aiohttp` client session.
  - `url`: The URL to make the API call.
  - `retries`: The number of times to retry.
  - `backoff_factor`: The backoff factor for retries.
  - `**kwargs`: Additional arguments for the API call.
- **Returns:** The response from the API call, if successful; otherwise, `None`.

### `upload_file_with_retry(http_session: aiohttp.ClientSession, url: str, file_path: str, param_name: str = "file", additional_data: Dict[str, Any] = None, retries: int = 3) -> Any`

Uploads a file to a specified URL with a retry mechanism for handling failures.

- **Parameters:**
  - `http_session`: The HTTP session object to use for making the request.
  - `url`: The URL to which the file will be uploaded.
  - `file_path`: The path to the file that will be uploaded.
  - `param_name`: The name of the parameter expected by the server for the file upload.
  - `additional_data`: Additional data to be sent with the upload.
  - `retries`: The number of times to retry the upload in case of failure.
- **Returns:** The HTTP response object.



## StatusTracker Class

Keeps track of various task statuses within a system, including the number of tasks started, in progress, succeeded, failed, and those failed due to specific errors such as rate limiting and API errors.

### Attributes

- `num_tasks_started (int)`: The number of tasks that have been initiated.
- `num_tasks_in_progress (int)`: The number of tasks currently being processed.
- `num_tasks_succeeded (int)`: The number of tasks that have completed successfully.
- `num_tasks_failed (int)`: The number of tasks that have failed.
- `num_rate_limit_errors (int)`: The number of tasks that failed due to rate limiting.
- `num_api_errors (int)`: The number of tasks that failed due to API errors.
- `num_other_errors (int)`: The number of tasks that failed due to other errors.

### Examples

```python
tracker = StatusTracker()
tracker.num_tasks_started += 1
tracker.num_tasks_succeeded += 1
```

## BaseRateLimiter Class

An abstract base class for implementing rate limiters, providing a structure for rate limiters including the replenishment of request and token capacities at regular intervals.

### Attributes

- `interval (int)`: The time interval in seconds for replenishing capacities.
- `max_requests (int)`: The maximum number of requests allowed per interval.
- `max_tokens (int)`: The maximum number of tokens allowed per interval.
- `available_request_capacity (int)`: The current available request capacity.
- `available_token_capacity (int)`: The current available token capacity.
- `rate_limit_replenisher_task (Optional[asyncio.Task[NoReturn]])`: The asyncio task for replenishing capacities.

### Methods

- `start_replenishing()`: Starts the replenishment of rate limit capacities at regular intervals.
- `stop_replenishing()`: Stops the replenishment task.
- `request_permission(required_tokens)`: Requests permission to make an API call, returning True if allowed.

## SimpleRateLimiter Class

A simple implementation of a rate limiter that inherits from `BaseRateLimiter`.

## EndPoint Class

Represents an API endpoint with rate limiting capabilities, encapsulating details such as the endpoint path, rate limiter class, and configuration parameters.

### Attributes

- `endpoint (str)`: The API endpoint path.
- `rate_limiter_class (Type[BaseRateLimiter])`: The class used for rate limiting requests to the endpoint.
- `max_requests (int)`: The maximum number of requests allowed per interval.
- `max_tokens (int)`: The maximum number of tokens allowed per interval.
- `interval (int)`: The time interval in seconds for replenishing rate limit capacities.
- `config (Dict)`: Configuration parameters for the endpoint.
- `rate_limiter (Optional[BaseRateLimiter])`: The rate limiter instance for this endpoint.

### Methods

- `init_rate_limiter()`: Initializes the rate limiter for the endpoint.

## BaseService Class

^4350a9

Base class for services interacting with API endpoints, providing a foundation for services that need to make API calls with rate limiting.

### Attributes

- `api_key (Optional[str])`: The API key used for authentication.
- `schema (Dict[str, Any])`: The schema defining the service's endpoints.
- `status_tracker (StatusTracker)`: The object tracking the status of API calls.
- `endpoints (Dict[str, EndPoint])`: A dictionary of endpoint objects.

### Methods

- `init_endpoint(endpoint_)`: Initializes the specified endpoint or all endpoints if none is specified.

- `call_api(payload, endpoint, method, **kwargs)`: Calls the specified API endpoint with the given payload and method. Requires the endpoint to have been initialized.

### Examples

```python
# Assuming an initialized BaseService instance and endpoint
payload = {'data': 'example'}
response = await service.call_api(payload, 'your_endpoint', 'post')
```

## PayloadPackage Class

A utility class for creating payloads for different types of API operations, such as chat completions and fine-tuning.

### Static Methods

- `chat_completion(messages, llmconfig, schema, **kwargs)`: Creates a payload for the chat completion operation.
  - **Parameters:**
    - `messages`: The messages to include in the chat completion.
    - `llmconfig`: Configuration for the language model.
    - `schema`: The schema describing required and optional fields.
    - `**kwargs`: Additional keyword arguments.
  - **Returns:** The constructed payload.

- `fine_tuning(training_file, llmconfig, schema, **kwargs)`: Creates a payload for the fine-tuning operation.
  - **Parameters:**
    - `training_file`: The file containing training data.
    - `llmconfig`: Configuration for the language model.
    - `schema`: The schema describing required and optional fields.
    - `**kwargs`: Additional keyword arguments.
  - **Returns:** The constructed payload.

### Examples

```python
# Example for creating a chat completion payload
messages = [{"role": "user", "content": "Hello!"}]
llmconfig = {"model": "gpt-3.5-turbo"}
schema = {
  "required": ["model"],
  "optional": ["temperature", "max_tokens"]
}
payload = PayloadPackage.chat_completion(messages, llmconfig, schema, temperature=0.7)
```


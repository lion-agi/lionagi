


# CallDecorator Class API Reference

The `CallDecorator` class offers a collection of decorators to enhance function calls, particularly for asynchronous functions, with additional behaviors like timeouts, retries, throttling, and caching. 

## Timeout Decorator

Applies a timeout to an asynchronous function call, raising an `asyncio.TimeoutError` if the specified duration is exceeded.

### Usage

```python
@CallDecorator.timeout(5)
async def long_running_task():
    await asyncio.sleep(10)
    return "Completed"
```

### Parameters

- `timeout (int)`: The maximum execution time allowed for the decorated function, in seconds.

## Retry Decorator

Automatically retries a function on failure, with configurable retries, delay, and exponential backoff. Useful for handling transient issues like network connectivity problems.

### Usage

```python
@CallDecorator.retry(retries=2, delay=1, backoff_factor=2)
async def fetch_data():
    raise ConnectionError("Temporary failure")
```

### Parameters

- `retries (int)`: The number of retry attempts.
- `delay (float)`: The initial delay between retries, in seconds.
- `backoff_factor (float)`: The multiplier applied to the delay for each subsequent retry.

## Default Decorator

Returns a default value in case the decorated function raises an exception, allowing for graceful error handling.

### Usage

```python
@CallDecorator.default(default_value="Fetch failed")
async def get_resource():
    raise RuntimeError("Resource not available")
```

### Parameters

- `default_value (Any)`: The value to return if the decorated function raises an exception.

Stay tuned for Part 2, where we will cover additional decorators provided by the `CallDecorator` class, including `throttle`, `map`, and `compose`, which offer further capabilities to manage and enhance function execution.


## Throttle Decorator

Limits the execution frequency of a function, ensuring it does not exceed one call per specified period. Useful for rate-limiting API calls or operations that should not be invoked too frequently.

### Usage

```python
@CallDecorator.throttle(2)
async def fetch_data():
    # Fetch data implementation
```

### Parameters

- `period (int)`: The minimum time interval, in seconds, between consecutive calls.

## Map Decorator

Applies a specified mapping function to each element in the list returned by the decorated function. Ideal for transforming data or applying a consistent operation to a list of items.

### Usage

```python
@CallDecorator.map(lambda x: x.upper())
async def get_names():
    return ["alice", "bob", "charlie"]
```

### Parameters

- `function (Callable[[Any], Any])`: A mapping function to apply to each element of the list.

## Compose Decorator

Sequentially applies multiple functions, where the output of one function becomes the input to the next. Facilitates function composition for chaining operations.

### Usage

```python
def double(x): return x * 2
def increment(x): return x + 1

@CallDecorator.compose(increment, double)
def start_value(x):
    return x
```

### Parameters

- `*functions (Callable[[Any], Any])`: Functions to be composed together.

## PrePostProcess Decorator

Applies preprocessing and postprocessing steps to a function, modifying arguments before the call and the result after the call.

### Usage

```python
@CallDecorator.pre_post_process(lambda x: x - 1, lambda x: x * 2)
async def process_value(x):
    return x + 2
```

### Parameters

- `preprocess (Callable[..., Any])`: A function to preprocess the arguments.
- `postprocess (Callable[..., Any])`: A function to postprocess the result.

## Cache Decorator

Caches the results of a function for a specified time-to-live (TTL), improving efficiency for I/O bound or computationally intensive operations.

### Usage

```python
@CallDecorator.cache(ttl=10)
async def fetch_data(key):
    # Simulate a database fetch
    return "data for " + key
```

### Parameters

- `ttl (int)`: The time-to-live of the cache entries in seconds.
- `maxsize (Optional[int])`: The maximum size of the cache for synchronous functions.

## Filter Decorator

Filters the list result of a function based on a given predicate, allowing for selective inclusion of elements in the final result.

### Usage

```python
@CallDecorator.filter(lambda x: x % 2 == 0)
async def get_even_numbers():
    return [1, 2, 3, 4, 5]
```

### Parameters

- `predicate (Callable[[Any], bool])`: A function to evaluate each item. Items for which the predicate returns True are included in the final result.

## Reduce Decorator

Applies a reduction to the list result of a function, combining all items into a single value using the specified reduction function. Ideal for aggregating results or cumulative operations.

### Usage

```python
@CallDecorator.reduce(lambda x, y: x + y, 0)
async def sum_numbers():
    return [1, 2, 3, 4]
```

### Parameters

- `function (Callable[[Any, Any], Any])`: The reduction function to apply to the list.
- `initial (Any)`: The initial value for the reduction process.

## Max Concurrency Decorator

Limits the number of concurrent executions of an asynchronous function to prevent overloading resources or hitting API rate limits.

### Usage

```python
@CallDecorator.max_concurrency(3)
async def process_data(item):
    # Asynchronous processing logic
```

### Parameters

- `limit (int)`: The maximum number of concurrent executions allowed.

## Force Async Decorator

Transforms a synchronous function into an asynchronous one, running it in a separate thread to integrate it into asynchronous workflows without blocking the event loop.

### Usage

```python
@CallDecorator.force_async
def compute_heavy_operation():
    # CPU-intensive logic
```


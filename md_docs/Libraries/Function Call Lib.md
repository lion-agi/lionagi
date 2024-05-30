# Function Utility API Reference

This module provides a collection of utility functions for working with functions, including decorators for enhancing function behavior and helpers for calling functions with various patterns.

## Functions:

### `lru_cache`
`(*args, **kwargs) -> Callable`

A wrapper around `functools.lru_cache` for caching function results.

Parameters:
- `*args`: Positional arguments to pass to `functools.lru_cache`.
- `**kwargs`: Keyword arguments to pass to `functools.lru_cache`.

Returns:
Callable: A decorator that caches the results of a function.

### `lcall`
`(input_: Any, /, func: Callable, *, flatten: bool = False, dropna: bool = False, **kwargs) -> list[Any]`

Applies a function to each element of the input list, with options to flatten results and drop None values.

Parameters:
- `input_` (Any): The input list or iterable to process. Each element will be passed to the provided `func` Callable.
- `func` (Callable): The function to apply to each element of `input_`. This function can be any Callable that accepts the elements of `input_` as arguments.
- `flatten` (bool): If True, the resulting list is flattened. Useful when `func` returns a list. Defaults to False.
- `dropna` (bool): If True, None values are removed from the final list. Defaults to False.
- `**kwargs`: Additional keyword arguments to be passed to `func`.

Returns:
list: The list of results after applying `func` to each input element, modified according to `flatten` and `dropna` options.

### `async alcall`
`(input_: Any | None = None, func: Callable = None, *, flatten: bool = False, dropna=False, **kwargs) -> list[Any]`

Asynchronously applies a function to each element in the input.

Parameters:
- `input_` (Any | None): The input to process. Defaults to None, which requires `func` to be capable of handling the absence of explicit input.
- `func` (Callable): The asynchronous function to apply. Defaults to None.
- `flatten` (bool): Whether to flatten the result. Useful when `func` returns a list or iterable that should be merged into a single list. Defaults to False.
- `**kwargs`: Keyword arguments to pass to the function.

Returns:
`list[Any]`: A list of results after asynchronously applying the function to each element of the input, potentially flattened.

### `async mcall`
`(input_: Any, /, func: Any, *, explode: bool = False, **kwargs) -> tuple[Any]`

Asynchronously maps a function or functions over an input or inputs.

Parameters:
- `input_` (Any): The input or inputs to process.
- `func` (Any): The function or functions to apply.
- `explode` (bool): Whether to apply each function to each input. Defaults to False.
- `**kwargs`: Keyword arguments to pass to the function.

Returns:
`tuple[Any]`: A tuple of results after applying the function(s).

### `async bcall`
`(input_: Any, /, func: Callable, *, batch_size: int, **kwargs) -> list[Any]`

Asynchronously calls a function on batches of inputs.

Parameters:
- `input_` (Any): The input to process.
- `func` (Callable): The function to apply.
- `batch_size` (int): The size of each batch.
- `**kwargs`: Keyword arguments to pass to the function.

Returns:
`list[Any]`: A list of results after applying the function in batches.

### `async tcall`
`(func: Callable, *args, delay: float = 0, err_msg: str | None = None, ignore_err: bool = False, timing: bool = False, timeout: float | None = None, **kwargs) -> Any`

Asynchronously executes a function with an optional delay, error handling, and timing.

Parameters:
- `func` (Callable): The asynchronous function to be called.
- `*args`: Positional arguments to pass to the function.
- `delay` (float): Time in seconds to wait before executing the function. Defaults to 0.
- `err_msg` (str | None): Custom error message to display if an error occurs. Defaults to None.
- `ignore_err` (bool): If True, suppresses any errors that occur during function execution, optionally returning a default value. Defaults to False.
- `timing` (bool): If True, returns a tuple containing the result of the function and the execution duration in seconds. Defaults to False.
- `timeout` (float | None): Maximum time in seconds allowed for the function execution. If the execution exceeds this time, a timeout error is raised. Defaults to None.
- `**kwargs`: Keyword arguments to pass to the function.

Returns:
Any: The result of the function call. If `timing` is True, returns a tuple of (result, execution duration).

### `async rcall`

^d5f3ae

`(func: Callable, *args, retries: int = 0, delay: float = 1.0, backoff_factor: float = 2.0, default: Any = None, timeout: float | None = None, **kwargs) -> Any`

Asynchronously retries a function call with exponential backoff.

Parameters:
- `func` (Callable): The asynchronous function to retry.
- `*args`: Positional arguments for the function.
- `retries` (int): The number of retry attempts before giving up. Defaults to 0.
- `delay` (float): Initial delay between retries in seconds. Defaults to 1.0.
- `backoff_factor` (float): Multiplier for the delay between retries, for exponential backoff. Defaults to 2.0.
- `default` (Any): A value to return if all retries fail. Defaults to None.
- `timeout` (float | None): Maximum duration in seconds for each attempt. Defaults to None.
- `**kwargs`: Keyword arguments for the function.

Returns:
Any: The result of the function call if successful within the retry attempts, otherwise the `default` value if specified.

## Classes:

### `CallDecorator`

Provides a collection of decorators to enhance asynchronous function calls with additional behaviors such as timeouts, retries, throttling, and more. These decorators are designed to support both synchronous and asynchronous functions, allowing for flexible and efficient execution patterns in a variety of contexts.

Static Methods:

#`timeout`
`(timeout: int) -> Callable`
Applies a timeout to an asynchronous function call, ensuring that the function execution completes within the specified duration.

#`retry`
`(retries: int = 3, delay: float = 2.0, backoff_factor: float = 2.0) -> Callable`
Decorates an asynchronous function to automatically retry on failure, with configurable retries, delay, and exponential backoff.

#`default`
`(default_value: Any) -> Callable`
Decorates an asynchronous function to return a default value in case of an exception, allowing the function to gracefully handle errors without interrupting the application flow.

#`throttle`
`(period: int) -> Callable`
Decorates an asynchronous function to limit its execution frequency to not exceed one call per specified period.

#`map`
`(function: Callable[[Any], Any]) -> Callable`
Decorates an asynchronous function to apply a specified mapping function to each element in the list returned by the decorated function.

#`compose`
`(*functions: Callable[[Any], Any]) -> Callable`
Creates a decorator to sequentially apply multiple functions, where the output of one function becomes the input to the next.

#`pre_post_process`
`(preprocess: Callable[..., Any] = None, postprocess: Callable[..., Any] = None, preprocess_args=[], preprocess_kwargs={}, postprocess_args=[], postprocess_kwargs={}) -> Callable`
Decorates a function with preprocessing and postprocessing steps, allowing for modifications to the arguments before the function call and to the result after the function call.

#`cache`
`(func: Callable, ttl=600, maxsize=None) -> Callable`
Decorates a function (synchronous or asynchronous) to cache its results for a specified time-to-live (TTL).

#`filter`
`(predicate: Callable[[Any], bool]) -> Callable`
Decorates a function to filter its list result based on a given predicate.

#`reduce`
`(function: Callable[[Any, Any], Any], initial: Any) -> Callable`
Decorates a function to apply a reduction to its list result, combining all items in the list into a single value using the specified reduction function.

#`max_concurrency`
`(limit: int = 5) -> Callable`
Limits the number of concurrent executions for an asynchronous function to ensure that no more than a specified number of instances of the function run simultaneously.

#`force_async(fn) -> Callable`
Converts a synchronous function into an asynchronous function by executing it in a separate thread.

### `Throttle`

A class that provides a throttling mechanism for function calls.

Attributes:
- `period` (int): The minimum time period (in seconds) between successive calls.

Methods:
- `__call__(self, func: Callable[..., Any]) -> Callable[..., Any]`: Decorates a synchronous function with the throttling mechanism.
- `async __call_async__(self, func: Callable[..., Any]) -> Callable[..., Any]`: Decorates an asynchronous function with the throttling mechanism.

## Additional Utility Functions:

### `async call_handler(func: Callable, *args, error_map: dict[type, Callable] = None, **kwargs) -> Any`

Calls a function with error handling, supporting both synchronous and asynchronous functions.

Parameters:
- `func` (Callable): The function to call.
- `*args`: Positional arguments to pass to the function.
- `error_map` (dict[type, Callable]): A dictionary mapping error types to handler functions.
- `**kwargs`: Keyword arguments to pass to the function.

Returns:
Any: The result of the function call.

### `is_coroutine_func(func: Callable) -> bool`

Checks if the specified function is an asyncio coroutine function.

Parameters:
- `func` (Callable): The function to check for coroutine compatibility.

Returns:
bool: True if `func` is an asyncio coroutine function, False otherwise.

## Usage Examples

```python
import asyncio
from lionagi.libs.func_call import lcall, alcall, mcall, bcall, tcall, rcall, CallDecorator

# Example usage of lcall
result = lcall([1, 2, 3], lambda x: x * 2)
print(result)  # Output: [2, 4, 6]

# Example usage of alcall
async def square(x):
    return x * x

result = await alcall([1, 2, 3], square)
print(result)  # Output: [1, 4, 9]

# Example usage of mcall
async def add_one(x):
    return x + 1

result = await mcall([1, 2, 3], add_one)
print(result)  # Output: (2, 3, 4)

# Example usage of bcall
async def sum_batch(batch):
    return sum(batch)

result = await bcall([1, 2, 3, 4], sum_batch, batch_size=2)
print(result)  # Output: [3, 7]

# Example usage of tcall
async def example_func(x):
    return x

result = await tcall(example_func, 5, timing=True)
print(result)  # Output: (5, duration)

# Example usage of rcall
async def flaky_function():
    raise Exception("Temporary failure")

result = await rcall(flaky_function, retries=3, delay=1, default="Default value")
print(result)  # Output: "Default value"

# Example usage of CallDecorator
@CallDecorator.timeout(5)
async def long_running_task():
    await asyncio.sleep(10)

@CallDecorator.retry(retries=2, delay=1)
async def flaky_task():
    raise Exception("Temporary failure")

@CallDecorator.cache(ttl=10)
async def cached_task(key):
    return f"Result for {key}"

# Run the examples
asyncio.run(long_running_task())  # Raises asyncio.TimeoutError after 5 seconds
asyncio.run(flaky_task())  # Retries the task up to 2 times
result = asyncio.run(cached_task("example"))
print(result)  # Output: "Result for example"
```

These examples demonstrate the usage of various functions and decorators provided by the `func_call` module. The functions support both synchronous and asynchronous execution, allowing for flexible and efficient function call patterns.


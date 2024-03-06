```
import lionagi.libs.ln_func_call as func_call
```

## Methods Overview

### `lcall`

Applies a function to each element of the input list, with options to flatten results and drop `None` values.

#### Arguments

- `input_ (Any)`: The input list or iterable to process. Each element will be passed to the provided `func` Callable.
- `func (Callable)`: The function to apply to each element of `input_`.
- `flatten (bool, optional)`: If True, the resulting list is flattened. Defaults to False.
- `dropna (bool, optional)`: If True, `None` values are removed from the final list. Defaults to False.
- `**kwargs`: Additional keyword arguments to be passed to `func`.

#### Returns

- `list[Any]`: The list of results after applying `func` to each input element, modified according to `flatten` and `dropna` options.

### `alcall`

Asynchronously applies a function to each element in the input.

#### Arguments

- `input_ (Any, optional)`: The input to process. Defaults to None.
- `func (Callable, optional)`: The asynchronous function to apply. Defaults to None.
- `flatten (bool, optional)`: Whether to flatten the result. Defaults to False.
- `dropna (bool, optional)`: Whether to drop None values from the result. Defaults to False.
- `**kwargs`: Keyword arguments to pass to the function.

#### Returns

- `list[Any]`: A list of results after asynchronously applying the function to each element of the input, potentially flattened.

### `mcall`

Asynchronously map a function or functions over an input or inputs.

#### Arguments

- `input_ (Any)`: The input or inputs to process.
- `func (Any)`: The function or functions to apply.
- `explode (bool, optional)`: Whether to apply each function to each input. Default is False.
- `**kwargs`: Keyword arguments to pass to the function.

#### Returns

- `tuple[Any]`: A list of results after applying the function(s).

## Examples

### Applying a Function to Each Element

```python
# Apply a doubling function to each element:
results = lcall([1, 2, 3], lambda x: x * 2)
print(results)  # Output: [2, 4, 6]
```

### Asynchronously Applying a Function

```python
# Example function to be used with `alcall`
async def square(x):
    return x * x

# Usage of `alcall` to apply `square` function to each element asynchronously
async def run_alcall():
    results = await alcall([1, 2, 3], square)
    print(results)  # Output: [1, 4, 9]

# Remember to run this inside an asyncio event loop
```

### Asynchronously Mapping Functions

```python
# Example function for use with `mcall`
async def add_one(x):
    return x + 1

# Using `mcall` to apply `add_one` to each element
async def run_mcall():
    results = await mcall([1, 2, 3], add_one)
    print(results)  # Output: (2, 3, 4)

# Ensure this is executed within an asyncio event loop
```


### `bcall`

Asynchronously calls a function on batches of inputs, facilitating efficient batch processing.

#### Arguments

- `input_ (Any)`: The inputs to process.
- `func (Callable)`: The function to apply to each batch.
- `batch_size (int)`: The size of each batch.
- `**kwargs`: Keyword arguments to pass to the function.

#### Returns

- `list[Any]`: A list of results after applying the function in batches.

### `tcall`

Asynchronously executes a function with an optional delay, error handling, and execution timing, offering precise control over function invocation.

#### Arguments

- `func (Callable)`: The asynchronous function to be called.
- `delay (float, optional)`: Time in seconds to wait before executing the function.
- `err_msg (str | None, optional)`: Custom error message if an error occurs.
- `ignore_err (bool, optional)`: If True, suppresses any errors that occur during function execution.
- `timing (bool, optional)`: If True, returns the execution duration along with the result.
- `timeout (float | None, optional)`: Maximum time allowed for the function execution.
- `**kwargs`: Keyword arguments to pass to the function.

#### Returns

- `Any`: The result of the function call, or a tuple of (result, execution duration) if timing is enabled.

### `rcall`

Retries a function call with exponential backoff, ideal for dealing with operations that may fail due to transient issues.

#### Arguments

- `func (Callable)`: The function to retry.
- `retries (int, optional)`: The number of retry attempts.
- `delay (float, optional)`: Initial delay between retries.
- `backoff_factor (float, optional)`: Multiplier for the delay between retries.
- `default (Any, optional)`: A value to return if all retries fail.
- `timeout (float | None, optional)`: Maximum time allowed for each attempt.
- `**kwargs`: Keyword arguments to pass to the function.

#### Returns

- `Any`: The result of the function call if successful, otherwise the `default` value.

## Examples

### Batch Processing with Asynchronous Function

```python
# Define an async function for demonstration
async def sum_batch(batch):
    return sum(batch)

# Use `bcall` for batch processing
async def run_bcall():
    input_data = [1, 2, 3, 4, 5, 6]
    results = await bcall(input_data, sum_batch, batch_size=2)
    print(results)  # Output: [3, 7, 11] since the input is processed in batches [1, 2], [3, 4], [5, 6]

# This needs to be run inside an asyncio event loop
```

### Delayed Asynchronous Function Call with Timing

```python
# Example async function
async def sample_function(x):
    return x * x

# Use `tcall` to execute with delay and measure timing
async def run_tcall():
    result, execution_duration = await tcall(sample_function, 3, delay=1, timing=True)
    print(result, execution_duration)  # Outputs: 9 and the execution duration

# Remember to execute this within an asyncio event loop
```

### Retrying Asynchronous Function Call with Exponential Backoff

```python
# Simulate a fetch operation that might intermittently fail
async def fetch_data():
    raise Exception("temporary error")

# Use `rcall` for retrying with exponential backoff
async def run_rcall():
    try:
        result = await rcall(fetch_data, retries=3, delay=2, default="default value")
        print(result)
    except Exception as e:
        print(e)

# This should be run inside an asyncio event loop, will return "default value" after retries
```

Apologies for the oversight. Let's continue with the documentation of non-hidden utility methods from the `fun_call` library, focusing on those designed to facilitate asynchronous programming and enhance the functionality of function calls with advanced features like caching and error handling.

### `is_coroutine_func`

Checks if the specified function is an asyncio coroutine function, aiding in distinguishing between synchronous and asynchronous functions for proper execution handling.

#### Arguments

- `func (Callable)`: The function to check for coroutine compatibility.

#### Returns

- `bool`: True if `func` is an asyncio coroutine function, False otherwise.

### `call_handler`

Executes a function with error handling support, accommodating both synchronous and asynchronous functions. This method allows specifying custom error handlers for different types of exceptions, enhancing the robustness and error resilience of function calls.

#### Arguments

- `func (Callable)`: The function to call.
- `*args`: Positional arguments to pass to the function.
- `error_map (dict[type, Callable])`: Optional dictionary mapping error types to handler functions.
- `**kwargs`: Keyword arguments to pass to the function.

#### Returns

- `Any`: The result of the function call.



# `CallDecorator` Class

^37a7ed

```
from lionagi.libs.ln_func_call import CallDecorator as cd
```
Provides a collection of decorators to enhance function calls with additional behaviors such as timeouts, retries, caching, and preprocessing or postprocessing. These decorators support both synchronous and asynchronous functions, enabling flexible and efficient execution patterns.

#### Key Decorators

- `timeout`: Applies a timeout to an asynchronous function call.
- `retry`: Automatically retries a function call on failure with configurable retries, delay, and exponential backoff.
- `default`: Returns a default value if the decorated function raises an exception.
- `throttle`: Limits the execution frequency of a function to not exceed one call per specified period.
- `map`: Applies a specified mapping function to each element in the list returned by the decorated function.
- `compose`: Sequentially applies multiple functions, where the output of one function becomes the input to the next.
- `pre_post_process`: Decorates a function with preprocessing and postprocessing steps.
- `cache`: Caches the results of a function call for a specified time-to-live (TTL).
- `filter`: Filters the list result of a function based on a given predicate.
- `reduce`: Applies a reduction to the list result of a function, combining all items into a single value using the specified reduction function.
- `max_concurrency`: Limits the number of concurrent executions for an asynchronous function.

### Examples

#### Checking if a Function is a Coroutine

```python
async def async_func():
    pass

def sync_func():
    pass

print(is_coroutine_func(async_func))  # Output: True
print(is_coroutine_func(sync_func))    # Output: False
```

#### Using `CallDecorator` for Retries with Exponential Backoff

```python
@cd.retry(retries=3, delay=1, backoff_factor=2)
async def fetch_data():
    # Implementation that might fail transiently
    raise ConnectionError("Temporary failure")

# Executing `fetch_data` will automatically retry on ConnectionError, up to 3 times,
# with delays of 1s, 2s, and 4s respectively.
```

### Example: Using `compose`

The `compose` decorator allows for the sequential application of multiple functions, where the output of one function becomes the input to the next.

```python
def double(x):
    return x * 2

def increment(x):
    return x + 1

@cd.compose(double, increment)
def start_value(x):
    return x

print(start_value(3))  # Output: 8
```
In this example, `start_value(3)` initially returns `3`, which is then passed through `increment` resulting in `4`, and finally through `double` resulting in `8`.

### Example: Using `pre_post_process`

The `pre_post_process` decorator enables the application of preprocessing and postprocessing steps to a function's arguments and its return value, respectively.

```python
def preprocess(x):
    return x - 1

def postprocess(x):
    return x * 2

@cd.pre_post_process(preprocess, postprocess)
def process_value(x):
    return x + 2

print(process_value(5))  # Output: 12
```
Here, the input `5` is preprocessed to `4`, processed to `6`, and postprocessed to `12`.

### Example: Using `filter`

The `filter` decorator filters the list result of a function based on a given predicate.

```python
@cd.filter(lambda x: x % 2 == 0)
async def get_even_numbers():
    return [1, 2, 3, 4, 5]

# Assuming an asyncio event loop is available:
# asyncio.run(get_even_numbers()) would output [2, 4]
```
This function, when called, returns a list of even numbers `[2, 4]` after applying the filter.

### Example: Using `reduce`

The `reduce` decorator applies a reduction to the list result of a function, combining all items into a single value using the specified reduction function.

```python
@cd.reduce(lambda x, y: x + y, 0)
async def sum_numbers():
    return [1, 2, 3, 4]

# Assuming an asyncio event loop is available:
# asyncio.run(sum_numbers()) would output 10
```
This decorated function sums up the numbers in the list, resulting in `10`.


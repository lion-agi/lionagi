

# CallUtil API Reference

This document covers utility functions designed for data conversion, list manipulation, and asynchronous function handling

## to_list

Converts a given input to a list, with options to flatten nested lists and exclude `None` values.

### Signature

```python
def to_list(input_: Any, flatten: bool = True, dropna: bool = False) -> List[Any]
```

### Parameters

- `input_`: The input to be converted to a list. It can be of any type that is iterable or a single object. Nested lists are handled based on the `flatten` argument.
- `flatten`: Indicates whether to flatten nested lists. If `True`, nested lists will be converted into a flat list. Defaults to `True`.
- `dropna`: Determines whether `None` values should be removed from the list. If `True`, all `None` values are excluded. Defaults to `False`.

### Returns

A list converted from the input, potentially flattened and without `None` values, based on the provided arguments.

### Examples

- Convert and flatten a nested list, excluding `None` values:

```python
to_list([1, [2, None], 3], flatten=True, dropna=True)
# Output: [1, 2, 3]
```

- Convert a non-list input without flattening:

```python
to_list("hello", flatten=False)
# Output: ["hello"]
```

## lcall

Applies a function to each element of the input list, with options to flatten results and drop `None` values.

### Signature

```python
def lcall(input_: Any, func: Callable, flatten: bool = False, dropna: bool = False, **kwargs) -> List[Any]
```

### Parameters

- `input_`: The input list or iterable to process. Each element will be passed to the provided `func` callable.
- `func`: The function to apply to each element of `input_`. This function can be any callable that accepts the elements of `input_` as arguments.
- `flatten`: If `True`, the resulting list is flattened. Useful when `func` returns a list. Defaults to `False`.
- `dropna`: If `True`, `None` values are removed from the final list. Defaults to `False`.
- `**kwargs`: Additional keyword arguments to be passed to `func`.

### Returns

The list of results after applying `func` to each input element, modified according to `flatten` and `dropna` options.

### Examples

- Apply a doubling function to each element:

```python
lcall([1, 2, 3], lambda x: x * 2)
# Output: [2, 4, 6]
```

- Apply a function that returns lists, then flatten the result:

```python
lcall([1, 2, None], lambda x: [x, x] if x else x, flatten=True, dropna=True)
# Output: [1, 1, 2, 2]
```

## is_coroutine_func

Checks if the specified function is an asyncio coroutine function.

### Signature

```python
def is_coroutine_func(func: Callable) -> bool
```

### Parameters

- `func`: The function to check for coroutine compatibility.

### Returns

`True` if `func` is an asyncio coroutine function, `False` otherwise.

### Examples

- Check if a function is coroutine-enabled:

```python
async def async_func(): pass
is_coroutine_func(async_func)
# Output: True

def sync_func(): pass
is_coroutine_func(sync_func)
# Output: False
```


## alcall

Asynchronously applies a function to each element in the input.

### Signature

```python
async def alcall(input_: Any = None, func: Callable = None, flatten: bool = False, **kwargs) -> List[Any]
```

### Parameters

- `input_`: The input to process. It defaults to `None`, which requires `func` to be capable of handling the absence of explicit input.
- `func`: The asynchronous function to apply. It defaults to `None`.
- `flatten`: Whether to flatten the result. Useful when `func` returns a list or iterable that should be merged into a single list. Defaults to `False`.
- `**kwargs`: Keyword arguments to pass to the function.

### Returns

A list of results after asynchronously applying the function to each element of the input, potentially flattened.

### Examples

- Asynchronously apply a squaring function to each element:

```python
async def square(x): return x * x
await alcall([1, 2, 3], square)
# Output: [1, 4, 9]
```

## mcall

Asynchronously maps a function or functions over an input or inputs.

### Signature

```python
async def mcall(input_: Any, func: Any, explode: bool = False, **kwargs) -> tuple[Any]
```

### Parameters

- `input_`: The input or inputs to process.
- `func`: The function or functions to apply.
- `explode`: Whether to apply each function to each input. The default is `False`.
- `**kwargs`: Keyword arguments to pass to the function.

### Returns

A tuple of results after applying the function(s).

### Examples

- Asynchronously apply a function to each element of an input list:

```python
async def add_one(x): return x + 1
await mcall([1, 2, 3], add_one)
# Output: [2, 3, 4]
```

## bcall

Asynchronously calls a function on batches of inputs.

### Signature

```python
async def bcall(input_: Any, func: Callable, batch_size: int, **kwargs) -> List[Any]
```

### Parameters

- `input_`: The input to process.
- `func`: The function to apply.
- `batch_size`: The size of each batch.
- `**kwargs`: Keyword arguments to pass to the function.

### Returns

A list of results after applying the function in batches.

### Examples

- Asynchronously sum batches of numbers:

```python
async def sum_batch(batch): return sum(batch)
await bcall([1, 2, 3, 4], sum_batch, batch_size=2)
# Output: [3, 7]
```



## tcall

Asynchronously executes a function with an optional delay, error handling, and timing.

### Signature

```python
async def tcall(func: Callable, *args, delay: float = 0, err_msg: Optional[str] = None, ignore_err: bool = False, timing: bool = False, timeout: Optional[float] = None, **kwargs) -> Any
```

### Parameters

- `func`: The asynchronous function to be called.
- `*args`: Positional arguments to pass to the function.
- `delay`: Time in seconds to wait before executing the function. Defaults to `0`.
- `err_msg`: Custom error message to display if an error occurs. Defaults to `None`.
- `ignore_err`: If `True`, suppresses any errors that occur during function execution, optionally returning a default value. Defaults to `False`.
- `timing`: If `True`, returns a tuple containing the result of the function and the execution duration in seconds. Defaults to `False`.
- `timeout`: Maximum time in seconds allowed for the function execution. Defaults to `None`.
- `**kwargs`: Keyword arguments to pass to the function.

### Returns

The result of the function call. If `timing` is `True`, returns a tuple of (result, execution duration).

### Examples

- Asynchronously execute a function after a delay, with timing:

```python
async def sample_function(x): return x * x
await tcall(sample_function, 3, delay=1, timing=True)
# Output: (9, execution_duration)
```

## rcall

Asynchronously retries a function call with exponential backoff.

### Signature

```python
async def rcall(func: Callable, *args, retries: int = 0, delay: float = 1.0, backoff_factor: float = 2.0, default: Any = None, timeout: Optional[float] = None, **kwargs) -> Any
```

### Parameters

- `func`: The asynchronous function to retry.
- `*args`: Positional arguments for the function.
- `retries`: The number of retry attempts before giving up. Defaults to `0`.
- `delay`: Initial delay between retries in seconds. Defaults to `1.0`.
- `backoff_factor`: Multiplier for the delay between retries, for exponential backoff. Defaults to `2.0`.
- `default`: A value to return if all retries fail. Defaults to `None`.
- `timeout`: Maximum duration in seconds for each attempt. Defaults to `None`.
- `**kwargs`: Keyword arguments for the function.

### Returns

The result of the function call if successful within the retry attempts, otherwise the `default` value if specified.

### Examples

- Asynchronously retry a function call, with exponential backoff and a default return value:

```python
async def fetch_data(): raise Exception("temporary error")
await rcall(fetch_data, retries=3, delay=2, default="default value")
# Output: "default value"
```




## Introduction to LionAGI Decorators

Decorators in LionAGI provide a powerful way to enhance the functionality of your function calls, both synchronous and asynchronous, without altering the function's core logic. This introductory guide covers the basics of using decorators to cache results and throttle function calls.

### Caching Results with `@cd.cache`

The `@cd.cache` decorator allows you to cache the results of your function calls. If the function is called again with the same parameters, it returns the cached result instead of executing again, significantly improving performance for repetitive calls with identical inputs.

**Example Usage:**

```python

from lionagi.libs import CallDecorator as cd


@cd.cache
def square_data(x):
    # Simulates a time-consuming operation
    return x ** 2


# First call caches the result
result = square_data(10)
print(result)  # Output: 100

# Second call retrieves result from cache
result = square_data(10)
print(result)  # Output: 100 (retrieved from cache)
```

### Throttling Function Calls with `@cd.throttle`

The `@cd.throttle` decorator limits the rate at which a function can be called. It ensures that there is a minimum delay between consecutive calls, useful for rate-limiting or managing resource utilization.

**Example Usage:**

```python
@cd.throttle(0.2)
def throttle_test(x):
    return x

# This loop will execute with a minimum delay of 0.2 seconds between each call
for i in range(5):
    print(throttle_test(i))
```

## Intermediate Decorators Guide

Building upon the basics, LionAGI's intermediate decorators offer more sophisticated control over function execution, including mapping, filtering, and composing multiple functions.

### Mapping with `@cd.map`

`@cd.map` applies a specified function to each element in the input list, allowing for concise and readable data transformations.

**Example Usage:**

```python
@cd.map(lambda x: x * x)
def square_numbers(numbers):
    return numbers

numbers = [1, 2, 3, 4, 5]
print(square_numbers(numbers))  # Output: [1, 4, 9, 16, 25]
```

### Filtering with `@cd.filter`

`@cd.filter` applies a predicate to the function's output, filtering the results based on the specified condition.

**Example Usage:**

```python
@cd.filter(predicate=lambda y: y < 10)
def filter_test(x):
    return [0, x**2]

print(filter_test(3))  # Output: [0]
```

### Composing Functions with `@cd.compose`

`@cd.compose` allows you to chain multiple functions together, where the output of each function is passed as the input to the next.

**Example Usage:**

```python
f1 = lambda x: x + 1
f2 = lambda x: x * 2

@cd.compose(f1, f2)
def compose_test(x):
    return x

print(compose_test(3))  # Output: 8
```

## Advanced Decorators Guide

For advanced use cases, LionAGI introduces decorators that handle asynchronous function specifics, such as concurrency control, timeout management, retry logic, and default value assignment on failure.

### Managing Maximum Concurrency with `@cd.max_concurrency`

`@cd.max_concurrency` controls the maximum number of concurrent executions of an asynchronous function, essential for managing load and preventing resource exhaustion.

**Example Usage:**

```python
@cd.max_concurrency(limit=2)
async def concurrent_test(x):
    # Simulate an async operation
    return x * 2

# This function will manage calls to ensure at most 2 are running concurrently
```

### Setting Timeouts with `@cd.timeout`

`@cd.timeout` decorator imposes a maximum execution time on a function, aborting it if the specified timeout is exceeded.

**Example Usage:**

```python
@cd.timeout(1)  # 1-second timeout
async def timeout_test():
    # Simulates a long-running operation
    await asyncio.sleep(2)
    return "Success"
```

### Implementing Retry Logic with `@cd.retry`

`@cd.retry` automatically retries a failing asynchronous function based on the defined policy, such as the maximum number of retries and delay strategy.

**Example Usage:**

```python
@cd.retry(retries=3, delay=0.1, backoff_factor=2)
async def retry_test(attempt):
    # Simulate a condition that may fail
    if attempt < 3:
        raise ValueError("Simulated error")
    return "Success"
```

### Providing a Default Value with `@cd.default`

`@cd.default` ensures that a function returns a predefined default value if it raises an exception, enhancing robustness.

**Example Usage:**

```python
@cd.default(default_value="Default Result")
async def default_test(may_fail):
    if may_fail:
        raise ValueError("Simulated error")
    return "Success"
```

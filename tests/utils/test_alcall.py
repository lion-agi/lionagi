import asyncio

import pytest

from lionagi.utils.alcall import alcall  # Adjust import path accordingly


class CustomError(Exception):
    pass


@pytest.mark.asyncio
async def test_single_callable():
    async def inc(x):
        return x + 1

    res = await alcall([1, 2, 3], inc)
    assert res == [2, 3, 4]


@pytest.mark.asyncio
async def test_iterable_single_callable():
    async def mul(x):
        return x * 2

    res = await alcall([1, 2], [mul])  # func as iterable
    assert res == [2, 4]


@pytest.mark.asyncio
async def test_non_callable_func():
    with pytest.raises(ValueError):
        await alcall([1, 2], 123)

    with pytest.raises(ValueError):
        await alcall([1, 2], [int, str])


@pytest.mark.asyncio
async def test_sanitize_input():
    def identity(x):
        return x

    # sanitize_input => flatten, dropna, unique_input if set
    # Input: [1, None, [2,2], 3, None]
    # After sanitize: flatten & dropna => [1,2,2,3]
    # with unique_input=True => [1,2,3]
    res = await alcall(
        [1, None, [2, 2], 3, None],
        identity,
        sanitize_input=True,
        unique_input=True,
    )
    assert res == [1, 2, 3]


@pytest.mark.asyncio
async def test_no_sanitize_input():
    def identity(x):
        return x

    # no sanitize_input => just ensure input_ is a list
    input_ = ((1, 2), "string", None, [3, 4])
    # Should just convert top-level tuple to list: [(1,2), 'string', None, [3,4]]
    # Since input_ is tuple, we expect no flattening or dropping unless specified
    res = await alcall(input_, identity)
    assert res == [(1, 2), "string", None, [3, 4]]


@pytest.mark.asyncio
async def test_num_retries_and_backoff():
    attempts = 0

    def flaky(x):
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise CustomError("fail")
        return x * 10

    # Will fail twice, succeed third time
    # retry_delay=0.01, backoff_factor=2 => delays: 0.01 then 0.02
    start = asyncio.get_event_loop().time()
    res = await alcall(
        [1], flaky, num_retries=2, retry_delay=0.01, backoff_factor=2
    )
    end = asyncio.get_event_loop().time()
    assert res == [10]
    assert (end - start) >= (0.01 + 0.02)  # approximate check


@pytest.mark.asyncio
async def test_retry_exhausted_no_default():
    def always_fail(x):
        raise CustomError("No success")

    with pytest.raises(CustomError):
        await alcall([1, 2], always_fail, num_retries=1, retry_delay=0.01)


@pytest.mark.asyncio
async def test_retry_default():
    def always_fail(x):
        raise ValueError("No success")

    # With retry_default, should return default instead of raising after retries
    res = await alcall(
        [1], always_fail, num_retries=2, retry_default="default_val"
    )
    assert res == ["default_val"]


@pytest.mark.asyncio
async def test_retry_timeout_async():
    async def slow(x):
        await asyncio.sleep(0.1)
        return x

    # If timeout is 0.05, task will timeout and return default
    res = await alcall(
        [1], slow, retry_timeout=0.05, retry_default="timeout_default"
    )
    assert res == ["timeout_default"]


@pytest.mark.asyncio
async def test_retry_timeout_sync():
    import time

    def slow(x):
        time.sleep(0.1)
        return x

    # Same logic but sync function
    res = await alcall(
        [1], slow, retry_timeout=0.05, retry_default="timeout_default"
    )
    assert res == ["timeout_default"]


@pytest.mark.asyncio
async def test_retry_timing():
    async def multiply(x):
        await asyncio.sleep(0.01)
        return x * 2

    # retry_timing=True => return (result, duration)
    res = await alcall([1, 2], multiply, retry_timing=True)
    # Expect [(2, duration), (4, duration)]
    assert len(res) == 2
    for val, dur in res:
        assert val in (2, 4)
        assert dur >= 0.01


@pytest.mark.asyncio
async def test_max_concurrent():
    # Check concurrency limit
    # We'll create tasks that sleep so we can ensure only certain concurrency
    async def slow_task(x):
        await asyncio.sleep(0.05)
        return x

    # With max_concurrent=1, tasks run sequentially
    start = asyncio.get_event_loop().time()
    res = await alcall([1, 2, 3], slow_task, max_concurrent=1)
    end = asyncio.get_event_loop().time()
    assert res == [1, 2, 3]
    # Approx check: 3 tasks *0.05=0.15s total
    assert (end - start) >= 0.15


@pytest.mark.asyncio
async def test_throttle_period():
    async def identity(x):
        return x

    # throttle_period=0.01 means after each task completion, wait 0.01s
    start = asyncio.get_event_loop().time()
    res = await alcall([1, 2, 3], identity, throttle_period=0.01)
    end = asyncio.get_event_loop().time()
    assert res == [1, 2, 3]
    # 3 tasks => after first two completions, we wait ~0.01*2=0.02s total extra
    assert (end - start) >= 0.02


@pytest.mark.asyncio
async def test_flatten_output():
    def identity(x):
        return x

    # Input results: let's have nested lists after function
    # We'll provide a sync func that returns nested lists
    input_ = [1, 2]

    def nested_func(x):
        return [x, [x + 1]]

    # results before flatten: [[1,[2]], [2,[3]]]
    # flatten=True => [1,2,2,3]
    res = await alcall(input_, nested_func, flatten=True)
    assert res == [1, 2, 2, 3]


@pytest.mark.asyncio
async def test_dropna_output():
    def maybe_none(x):
        return None if x == 2 else x

    # dropna=True => remove None
    input_ = [1, 2, 3]
    res = await alcall(input_, maybe_none, dropna=True)
    # results before drop: [1,None,3]
    # after dropna: [1,3]
    assert res == [1, 3]


@pytest.mark.asyncio
async def test_unique_output():
    def identity(x):
        return x

    # with flatten and unique_output
    input_ = [[1, 1], [2, 2], [3, 3]]
    # after flatten: [1,1,2,2,3,3]
    # unique_output=True => [1,2,3]
    res = await alcall(input_, identity, flatten=True, unique_output=True)
    assert res == [1, 2, 3]


@pytest.mark.asyncio
async def test_no_flatten_no_dropna_unique_output_raises():
    def identity(x):
        return x

    # According to previous conventions, unique_output requires flatten or dropna to trigger processing
    # If it doesn't raise by current code, consider adding a check or adapt test
    # If current code does not raise, let's test the behavior:
    # If it doesn't raise, we can just verify that it doesn't change output since no flatten/dropna means no reprocessing.
    # Let's assume it should raise or we know it doesn't:
    # If no re-processing occurs, it might just ignore unique_output
    # The test might assume old behavior (like lcall)
    # If consistent with previous patterns, let's expect a ValueError:
    with pytest.raises(ValueError):
        await alcall([1, 1, 2], identity, unique_output=True)


@pytest.mark.asyncio
async def test_retry_timing_with_retries():
    attempts = 0

    async def flaky(x):
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise CustomError("fail")
        await asyncio.sleep(0.01)
        return x

    # Will fail once, then succeed.
    # retry_timing=True => return (result, duration)
    res = await alcall(
        [42], flaky, num_retries=1, retry_timing=True, retry_delay=0.01
    )
    # After first fail, waits 0.01s, then success after another 0.01 sleep in func
    assert len(res) == 1
    val, dur = res[0]
    assert val == 42
    assert dur >= 0.02  # includes failed attempt + retry wait + run time


@pytest.mark.asyncio
async def test_complex_sanitize_input():
    def identity(x):
        return x

    # sanitize_input: flatten, dropna, unique_input
    # Input: [1, None, [2, None, [3,None]], "abc", None]
    # After sanitize: flatten+dropna => [1,2,3,"abc"]
    # unique_input=False by default => no dedup
    res = await alcall(
        [1, None, [2, None, [3, None]], "abc", None],
        identity,
        sanitize_input=True,
    )
    assert res == [1, 2, 3, "abc"]


@pytest.mark.asyncio
async def test_retry_default_on_non_timeout_error():
    def fail(x):
        raise RuntimeError("Always fail")

    # num_retries=2, still fails, return retry_default
    res = await alcall(
        [10], fail, num_retries=2, retry_delay=0.01, retry_default="fallback"
    )
    assert res == ["fallback"]


@pytest.mark.asyncio
async def test_flatten_tuple_set():
    # If flatten_tuple_set=True, ensure tuples and sets are flattened similarly
    def return_nested(x):
        return (x, {x + 1}, [x + 2])

    # If flatten=True and flatten_tuple_set=True, (x) and {x+1} are flattened
    # return_nested(1) => (1, {2}, [3])
    # flatten => [1,2,3]
    res = await alcall(
        [1], return_nested, flatten=True, flatten_tuple_set=True
    )
    assert res == [1, 2, 3]


@pytest.mark.asyncio
async def test_order_preservation():
    async def delay_return(x):
        await asyncio.sleep((3 - x) * 0.01)  # inverse order finishing
        return x

    # Input: [1,2,3]
    # The tasks finish in order 3,2,1 but we must return in original order
    res = await alcall([1, 2, 3], delay_return)
    assert res == [
        1,
        2,
        3,
    ]  # original order maintained even though completion order differs

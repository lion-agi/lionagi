import asyncio

import pytest

from lionagi.utils.tcall import tcall  # Adjust import path as necessary


class CustomError(Exception):
    pass


@pytest.mark.asyncio
async def test_sync_function_success():
    def add(x, y=0):
        return x + y

    result = await tcall(add, 1, y=2)
    assert result == 3


@pytest.mark.asyncio
async def test_async_function_success():
    async def mul(x, y=1):
        await asyncio.sleep(0.01)
        return x * y

    result = await tcall(mul, 2, y=5)
    assert result == 10


@pytest.mark.asyncio
async def test_timing():
    async def identity(x):
        await asyncio.sleep(0.01)
        return x

    res, duration = await tcall(identity, 100, timing=True)
    assert res == 100
    assert duration >= 0  # At least no negative times


@pytest.mark.asyncio
async def test_initial_delay():
    async def identity(x):
        return x

    start = asyncio.get_event_loop().time()
    res = await tcall(identity, "hello", initial_delay=0.05)
    end = asyncio.get_event_loop().time()
    assert res == "hello"
    assert (end - start) >= 0.05


@pytest.mark.asyncio
async def test_timeout_no_default():
    async def slow_task():
        await asyncio.sleep(0.1)
        return "done"

    with pytest.raises(asyncio.TimeoutError) as exc:
        await tcall(slow_task, timeout=0.01)
    assert "Timeout 0.01 seconds exceeded" in str(exc.value)


@pytest.mark.asyncio
async def test_timeout_with_default():
    async def slow_task():
        await asyncio.sleep(0.1)
        return "done"

    # If default is provided, return it on timeout
    result = await tcall(slow_task, timeout=0.01, default="timed_out")
    assert result == "timed_out"


@pytest.mark.asyncio
async def test_sync_timeout():
    import time

    def slow_sync():
        time.sleep(0.1)
        return "sync done"

    with pytest.raises(asyncio.TimeoutError):
        await tcall(slow_sync, timeout=0.01)


@pytest.mark.asyncio
async def test_sync_timeout_with_default():
    import time

    def slow_sync():
        time.sleep(0.1)
        return "sync done"

    result = await tcall(slow_sync, timeout=0.01, default="default_val")
    assert result == "default_val"


@pytest.mark.asyncio
async def test_error_with_no_default_no_error_map():
    def fail():
        raise CustomError("Boom!")

    with pytest.raises(RuntimeError) as exc:
        await tcall(fail)
    assert "An error occurred in async execution: Boom!" in str(exc.value)


@pytest.mark.asyncio
async def test_error_with_default():
    def fail():
        raise ValueError("Bad")

    # If default is given, return it instead of raising
    res = await tcall(fail, default="fallback")
    assert res == "fallback"


@pytest.mark.asyncio
async def test_error_with_error_map():
    def fail():
        raise CustomError("Custom fail")

    captured_errors = []

    def handle_custom(e: Exception):
        captured_errors.append(str(e))

    error_map = {CustomError: handle_custom}
    res = await tcall(fail, error_map=error_map)
    # Handler should have been called
    assert "Custom fail" in captured_errors[0]
    # When handler is called, we return None if not specified otherwise
    assert res is None


@pytest.mark.asyncio
async def test_error_with_error_map_non_matching():
    def fail():
        raise ValueError("Other error")

    # Non-matching error_map entry
    error_map = {CustomError: lambda e: None}
    with pytest.raises(RuntimeError) as exc:
        await tcall(fail, error_map=error_map)
    assert "An error occurred in async execution: Other error" in str(
        exc.value
    )


@pytest.mark.asyncio
async def test_error_with_error_msg():
    def fail():
        raise CustomError("Error here")

    with pytest.raises(RuntimeError) as exc:
        await tcall(fail, error_msg="Prefix")
    assert "Prefix Error: Error here" in str(exc.value)


@pytest.mark.asyncio
async def test_args_kwargs():
    def combine(x, y=0, z=0):
        return x + y + z

    res = await tcall(combine, 10, y=5, z=5)
    assert res == 20


@pytest.mark.asyncio
async def test_async_with_timing_and_error():
    async def fail():
        await asyncio.sleep(0.01)
        raise CustomError("Failing async")

    # With timing and default
    res, duration = await tcall(fail, default="default", timing=True)
    assert res == "default"
    assert duration >= 0


@pytest.mark.asyncio
async def test_async_with_timing_success():
    async def wait_and_return(x):
        await asyncio.sleep(0.02)
        return x * 2

    res, duration = await tcall(wait_and_return, 10, timing=True)
    assert res == 20
    assert duration >= 0.02  # Should include the sleep time


@pytest.mark.asyncio
async def test_initial_delay_and_timing():
    async def task(x):
        await asyncio.sleep(0.01)
        return x

    start = asyncio.get_event_loop().time()
    res, duration = await tcall(
        task, "delayed", initial_delay=0.02, timing=True
    )
    end = asyncio.get_event_loop().time()
    assert res == "delayed"
    # total should be at least ~0.03
    assert end - start >= 0.02
    assert duration >= 0.03  # includes initial_delay + task run


@pytest.mark.asyncio
async def test_zero_initial_delay():
    async def quick():
        return "quick"

    res = await tcall(quick, initial_delay=0)
    assert res == "quick"


@pytest.mark.asyncio
async def test_no_error_map_default_error_msg():
    # If error happens and no default, no error_map, custom error_msg
    def bad():
        raise RuntimeError("Internal Error")

    with pytest.raises(RuntimeError) as exc:
        await tcall(bad, error_msg="Custom prefix")
    assert "Custom prefix Error: Internal Error" in str(exc.value)


@pytest.mark.asyncio
async def test_undefined_default_is_raised():
    def fail():
        raise ValueError("No default set")

    # Should raise RuntimeError since default=Undefined
    with pytest.raises(RuntimeError) as exc:
        await tcall(fail)
    assert "An error occurred in async execution: No default set" in str(
        exc.value
    )

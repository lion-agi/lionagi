import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest

from lionagi.libs.func import tcall


async def async_func(x: int) -> int:
    await asyncio.sleep(0.1)
    return x + 1


def sync_func(x: int) -> int:
    return x + 1


async def async_func_with_error(x: int) -> int:
    await asyncio.sleep(0.1)
    if x == 3:
        raise ValueError("mock error")
    return x + 1


def sync_func_with_error(x: int) -> int:
    if x == 3:
        raise ValueError("mock error")
    return x + 1


async def async_func_with_kwargs(x: int, add: int) -> int:
    await asyncio.sleep(0.1)
    return x + add


@pytest.mark.asyncio
async def test_tcall_async_func():
    result = await tcall(async_func, 1)
    assert result == 2


@pytest.mark.asyncio
async def test_tcall_sync_func():
    result = await tcall(sync_func, 1)
    assert result == 2


@pytest.mark.asyncio
async def test_tcall_async_func_with_timing():
    result, duration = await tcall(async_func, 1, retry_timing=True)
    assert result == 2
    assert duration > 0


@pytest.mark.asyncio
async def test_tcall_sync_func_with_timing():
    result, duration = await tcall(sync_func, 1, retry_timing=True)
    assert result == 2
    assert duration > 0


@pytest.mark.asyncio
async def test_tcall_async_func_with_error():
    with pytest.raises(RuntimeError):
        await tcall(async_func_with_error, 3)


@pytest.mark.asyncio
async def test_tcall_sync_func_with_error():
    with pytest.raises(RuntimeError):
        await tcall(sync_func_with_error, 3)


@pytest.mark.asyncio
async def test_tcall_with_error_handling():
    async def mock_handler(e: Exception) -> str:
        return f"handled: {str(e)}"

    error_map = {ValueError: mock_handler}
    result = await tcall(async_func_with_error, 3, error_map=error_map)
    assert result is None  # Custom error handling does not change result


@pytest.mark.asyncio
async def test_tcall_with_initial_delay():
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await tcall(async_func, 1, initial_delay=0.5)
        mock_sleep.assert_any_call(0.5)
        assert result == 2


@pytest.mark.asyncio
async def test_tcall_with_timeout():
    with pytest.raises(asyncio.TimeoutError):
        await tcall(async_func, 1, retry_timeout=0.05)


@pytest.mark.asyncio
async def test_tcall_with_suppress_err():
    result = await tcall(
        async_func_with_error, 3, suppress_err=True, retry_default=0
    )
    assert result == 0


@pytest.mark.asyncio
async def test_tcall_with_kwargs():
    result = await tcall(async_func_with_kwargs, 1, add=2)
    assert result == 3


@pytest.mark.asyncio
async def test_tcall_with_generator():
    async def async_generator():
        for i in range(3):
            yield i

    result = await tcall(async_generator)
    assert isinstance(result, AsyncGenerator)


@pytest.mark.asyncio
async def test_tcall_with_class_method():
    class TestClass:
        async def async_method(self, x):
            await asyncio.sleep(0.1)
            return x * 2

    obj = TestClass()
    result = await tcall(obj.async_method, 5)
    assert result == 10


@pytest.mark.asyncio
async def test_tcall_with_lambda():
    result = await tcall(lambda x: x * 3, 4)
    assert result == 12


@pytest.mark.asyncio
async def test_tcall_with_recursive_function():
    async def async_factorial(n):
        if n == 0:
            return 1
        return n * await tcall(async_factorial, n - 1)

    result = await tcall(async_factorial, 5)
    assert result == 120


@pytest.mark.asyncio
async def test_tcall_performance():
    async def slow_function():
        await asyncio.sleep(0.5)
        return "Done"

    import time

    start = time.time()
    await tcall(slow_function)
    duration = time.time() - start
    assert 0.5 <= duration < 0.6

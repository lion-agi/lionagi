import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import patch

import pytest

from lionagi.libs.func.types import ucall


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


async def mock_handler(e: Exception) -> str:
    return f"handled: {str(e)}"


async def async_func_with_kwargs(x: int, add: int) -> int:
    await asyncio.sleep(0.1)
    return x + add


@pytest.mark.asyncio
async def test_ucall_with_async_func():
    result = await ucall(async_func, 1)
    assert result == 2


@pytest.mark.asyncio
async def test_ucall_with_sync_func():
    result = await ucall(sync_func, 1)
    assert result == 2


@pytest.mark.asyncio
async def test_ucall_with_async_func_with_error():
    with pytest.raises(ValueError):
        await ucall(async_func_with_error, 3)


@pytest.mark.asyncio
async def test_ucall_with_sync_func_with_error():
    with pytest.raises(ValueError):
        await ucall(sync_func_with_error, 3)


@pytest.mark.asyncio
async def test_ucall_with_error_handling():
    error_map = {ValueError: mock_handler}
    result = await ucall(async_func_with_error, 3, error_map=error_map)
    assert result == "handled: mock error"


@pytest.mark.asyncio
async def test_ucall_with_no_event_loop():
    with patch(
        "asyncio.get_running_loop",
        side_effect=RuntimeError("no running event loop"),
    ):
        result = await ucall(sync_func, 1)
        assert result == 2


@pytest.mark.asyncio
async def test_ucall_with_running_event_loop():
    result = await ucall(sync_func, 1)
    assert result == 2


@pytest.mark.asyncio
async def test_ucall_with_kwargs():
    result = await ucall(async_func_with_kwargs, 1, add=2)
    assert result == 3


@pytest.mark.asyncio
async def test_ucall_with_generator():
    async def async_generator():
        for i in range(3):
            yield i

    result = await ucall(async_generator)
    assert isinstance(result, AsyncGenerator)


@pytest.mark.asyncio
async def test_ucall_with_class_method():
    class TestClass:
        async def async_method(self, x):
            await asyncio.sleep(0.1)
            return x * 2

    obj = TestClass()
    result = await ucall(obj.async_method, 5)
    assert result == 10


@pytest.mark.asyncio
async def test_ucall_with_lambda():
    result = await ucall(lambda x: x * 3, 4)
    assert result == 12


@pytest.mark.asyncio
async def test_ucall_with_recursive_function():
    async def async_factorial(n):
        if n == 0:
            return 1
        return n * await ucall(async_factorial, n - 1)

    result = await ucall(async_factorial, 5)
    assert result == 120


@pytest.mark.asyncio
async def test_ucall_performance():
    async def slow_function():
        await asyncio.sleep(0.5)
        return "Done"

    import time

    start = time.time()
    await ucall(slow_function)
    duration = time.time() - start
    assert 0.5 <= duration < 0.6


# File: tests/test_ucall.py

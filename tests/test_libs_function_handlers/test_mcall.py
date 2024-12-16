import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from lionagi.libs.func.types import mcall


async def async_func(x: int) -> int:
    await asyncio.sleep(0.1)
    return x * 2


def sync_func(x: int) -> int:
    return x * 2


async def async_func_with_error(x: int) -> int:
    await asyncio.sleep(0.1)
    if x == 3:
        raise ValueError("mock error")
    return x * 2


def sync_func_with_error(x: int) -> int:
    if x == 3:
        raise ValueError("mock error")
    return x * 2


class TestMCallFunction(unittest.IsolatedAsyncioTestCase):
    async def test_mcall_single_func(self):
        inputs = [1, 2, 3, 4, 5]
        result = await mcall(inputs, async_func)
        self.assertEqual(result, [2, 4, 6, 8, 10])

    async def test_mcall_multiple_funcs_explode(self):
        inputs = [1, 2, 3, 4, 5]
        funcs = [async_func, async_func]
        results = await mcall(inputs, funcs, explode=True)
        self.assertEqual(results, [[2, 4, 6, 8, 10], [2, 4, 6, 8, 10]])

    async def test_mcall_multiple_funcs_no_explode(self):
        inputs = [1, 2, 3, 4, 5]
        funcs = [async_func, async_func, async_func, async_func, async_func]
        result = await mcall(inputs, funcs)
        self.assertEqual(result, [2, 4, 6, 8, 10])

    async def test_mcall_with_retries(self):
        inputs = [1, 2, 3, 4, 5]
        funcs = [async_func_with_error] * 5
        results = await mcall(inputs, funcs, num_retries=1, retry_default=0)
        self.assertEqual(results, [2, 4, 0, 8, 10])

    async def test_mcall_with_timeout(self):
        inputs = [1, 2, 3]
        with self.assertRaises(RuntimeError):
            await mcall(inputs, async_func, retry_timeout=0.05)

    async def test_mcall_with_error_handling(self):
        async def mock_handler(e: Exception) -> str:
            return f"handled: {str(e)}"

        error_map = {ValueError: mock_handler}
        inputs = [1, 2, 3, 4, 5]
        funcs = [async_func_with_error] * 5
        result = await mcall(inputs, funcs, error_map=error_map)
        self.assertEqual(result, [2, 4, "handled: mock error", 8, 10])

    async def test_mcall_with_max_concurrent(self):
        inputs = [1, 2, 3, 4, 5]
        result = await mcall(inputs, async_func, max_concurrent=1)
        self.assertEqual(result, [2, 4, 6, 8, 10])

    async def test_mcall_with_throttle_period(self):
        inputs = [1, 2, 3, 4, 5]
        result = await mcall(inputs, async_func, throttle_period=0.2)
        self.assertEqual(result, [2, 4, 6, 8, 10])

    async def test_mcall_with_initial_delay(self):
        inputs = [1, 2, 3]
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            result = await mcall(inputs, async_func, initial_delay=0.5)
            mock_sleep.assert_any_call(0.5)
            self.assertEqual(result, [2, 4, 6])

    async def test_mcall_with_kwargs(self):
        async def async_func_with_kwargs(x: int, add: int) -> int:
            await asyncio.sleep(0.1)
            return x + add

        inputs = [1, 2, 3, 4, 5]
        result = await mcall(inputs, async_func_with_kwargs, add=10)
        self.assertEqual(result, [11, 12, 13, 14, 15])


if __name__ == "__main__":
    unittest.main()

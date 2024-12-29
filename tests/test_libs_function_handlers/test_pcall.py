import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from lionagi.libs.func import pcall


async def async_func() -> int:
    await asyncio.sleep(0.1)
    return 2


def sync_func() -> int:
    return 2


async def async_func_with_error() -> int:
    await asyncio.sleep(0.1)
    raise ValueError("mock error")


def sync_func_with_error() -> int:
    raise ValueError("mock error")


async def mock_handler(e: Exception) -> str:
    return f"handled: {str(e)}"


class TestPCallFunction(unittest.IsolatedAsyncioTestCase):
    async def test_pcall_basic(self):
        funcs = [async_func for _ in range(5)]
        result = await pcall(funcs)
        self.assertEqual(result, [2, 2, 2, 2, 2])

    async def test_pcall_with_timing(self):
        funcs = [async_func for _ in range(5)]
        result = await pcall(funcs, retry_timing=True)
        for res, duration in result:
            self.assertTrue(duration > 0)
        self.assertEqual([res for res, duration in result], [2, 2, 2, 2, 2])

    async def test_pcall_with_retries(self):
        funcs = [async_func_with_error for _ in range(5)]
        result = await pcall(funcs, num_retries=1, retry_default=0)
        self.assertEqual(result, [0, 0, 0, 0, 0])

    async def test_pcall_with_error_handling(self):
        error_map = {ValueError: mock_handler}
        funcs = [async_func_with_error for _ in range(5)]
        result = await pcall(funcs, error_map=error_map)
        self.assertEqual(
            result,
            [
                "handled: mock error",
                "handled: mock error",
                "handled: mock error",
                "handled: mock error",
                "handled: mock error",
            ],
        )

    async def test_pcall_with_max_concurrent(self):
        funcs = [async_func for _ in range(5)]
        result = await pcall(funcs, max_concurrent=1)
        self.assertEqual(result, [2, 2, 2, 2, 2])

    async def test_pcall_with_throttle_period(self):
        funcs = [async_func for _ in range(5)]
        result = await pcall(funcs, throttle_period=0.2)
        self.assertEqual(result, [2, 2, 2, 2, 2])

    async def test_pcall_with_initial_delay(self):
        funcs = [async_func for _ in range(3)]
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            result = await pcall(funcs, initial_delay=0.5)
            mock_sleep.assert_any_call(0.5)
            self.assertEqual(result, [2, 2, 2])

    async def test_pcall_with_sync_func(self):
        funcs = [sync_func for _ in range(5)]
        result = await pcall(funcs)
        self.assertEqual(result, [2, 2, 2, 2, 2])


if __name__ == "__main__":
    unittest.main()

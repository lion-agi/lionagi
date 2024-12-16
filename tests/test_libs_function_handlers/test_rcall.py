import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from lionagi.libs.func import rcall


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


class TestRCallFunction(unittest.IsolatedAsyncioTestCase):
    async def test_rcall_basic(self):
        result = await rcall(async_func, 1, num_retries=2)
        self.assertEqual(result, 2)

    async def test_rcall_with_retries(self):
        result = await rcall(
            async_func_with_error, 3, num_retries=1, retry_default=0
        )
        self.assertEqual(result, 0)

    async def test_rcall_with_timeout(self):
        with self.assertRaises(RuntimeError):
            await rcall(async_func, 1, retry_timeout=0.05)

    async def test_rcall_with_error_handling(self):
        async def mock_handler(e: Exception) -> str:
            return f"handled: {str(e)}"

        error_map = {ValueError: mock_handler}
        result = await rcall(
            async_func_with_error, 3, num_retries=1, error_map=error_map
        )
        self.assertEqual(result, "handled: mock error")

    async def test_rcall_with_timing(self):
        result, duration = await rcall(async_func, 1, retry_timing=True)
        self.assertEqual(result, 2)
        self.assertTrue(duration > 0)

    async def test_rcall_with_initial_delay(self):
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await rcall(async_func, 1, initial_delay=0.5)
            mock_sleep.assert_any_call(0.5)

    async def test_rcall_with_backoff_factor(self):
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await rcall(
                async_func_with_error,
                3,
                num_retries=2,
                retry_delay=0.1,
                backoff_factor=2,
                retry_default=0,
            )
            mock_sleep.assert_any_call(0.1)
            mock_sleep.assert_any_call(0.2)

    async def test_rcall_with_kwargs(self):
        async def async_func_with_kwargs(x: int, add: int) -> int:
            await asyncio.sleep(0.1)
            return x + add

        result = await rcall(async_func_with_kwargs, 1, num_retries=2, add=2)
        self.assertEqual(result, 3)

    async def test_rcall_with_verbose(self):
        with patch("builtins.print") as mock_print:
            await rcall(
                async_func_with_error,
                3,
                num_retries=1,
                verbose_retry=True,
                retry_default=0,
            )
            mock_print.assert_any_call(
                "Attempt 1/2 failed: mock error, retrying..."
            )


if __name__ == "__main__":
    unittest.main()

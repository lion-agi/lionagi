import asyncio
import unittest

from lionagi.libs.func.types import (
    force_async,
    is_coroutine_func,
    max_concurrent,
    throttle,
)


# Mock and Helper Functions
def sync_func(x: int) -> int:
    return x + 1


async def async_func(x: int) -> int:
    await asyncio.sleep(0.1)
    return x + 1


def sync_func_with_error(x: int) -> int:
    if x == 3:
        raise ValueError("mock error")
    return x + 1


async def async_func_with_error(x: int) -> int:
    await asyncio.sleep(0.1)
    if x == 3:
        raise ValueError("mock error")
    return x + 1


def mock_handler(e: Exception) -> str:
    return f"handled: {str(e)}"


# Tests
class TestUtilityFunctions(unittest.IsolatedAsyncioTestCase):
    async def test_force_async(self):
        async_sync_func = force_async(sync_func)
        result = await async_sync_func(1)
        self.assertEqual(result, 2)

    async def test_is_coroutine_func(self):
        self.assertTrue(is_coroutine_func(async_func))
        self.assertFalse(is_coroutine_func(sync_func))

    # async def test_custom_error_handler(self):
    #     error_map = {ValueError: mock_handler}
    #     with self.assertLogs(level='ERROR') as log:
    #         try:
    #             raise ValueError("test error")
    #         except Exception as e:
    #             custom_error_handler(e, error_map)
    #     self.assertIn("handled: test error", log.output[0])

    async def test_max_concurrent(self):
        async_limited_func = max_concurrent(async_func, limit=1)
        results = await asyncio.gather(
            async_limited_func(1), async_limited_func(2)
        )
        self.assertEqual(results, [2, 3])

    async def test_throttle(self):
        throttled_func = throttle(async_func, period=0.5)
        results = await asyncio.gather(throttled_func(1), throttled_func(2))
        self.assertEqual(results, [2, 3])

    async def test_force_async_with_error(self):
        async_sync_func_with_error = force_async(sync_func_with_error)
        with self.assertRaises(ValueError):
            await async_sync_func_with_error(3)

    async def test_max_concurrent_with_error(self):
        async_limited_func_with_error = max_concurrent(
            async_func_with_error, limit=1
        )
        with self.assertRaises(ValueError):
            await asyncio.gather(
                async_limited_func_with_error(1),
                async_limited_func_with_error(3),
            )

    async def test_throttle_with_error(self):
        throttled_func_with_error = throttle(async_func_with_error, period=0.5)
        with self.assertRaises(ValueError):
            await asyncio.gather(
                throttled_func_with_error(1), throttled_func_with_error(3)
            )


if __name__ == "__main__":
    unittest.main()

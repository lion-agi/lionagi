import unittest
import asyncio
from unittest.mock import patch
import time
import functools
from time import sleep

from lionagi.lib.function_handlers import *
from lionagi.lib.function_handlers._util import *


class TestBCall(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    async def async_func(self, x):
        return x * 2

    async def error_func(self, x):
        if x == 3:
            raise ValueError("Test exception")
        return x * 2

    def test_bcall_success(self):
        inputs = [1, 2, 3, 4, 5]
        expected = [[2, 4], [6, 8], [10]]

        async def run_test():
            results = []
            async for batch_results in bcall(inputs, self.async_func, 2):
                results.append(batch_results)
            return results

        result = self.loop.run_until_complete(run_test())
        self.assertEqual(result, expected)

    def test_bcall_with_errors(self):
        inputs = [1, 2, 3, 4, 5]
        expected = [
            [2, 4],
            ["Test exception", 8],
            [10],
        ]

        async def run_test():
            results = []
            async for batch_results in bcall(
                inputs, self.error_func, 2, default="Test exception"
            ):
                results.append(batch_results)
            return results

        result = self.loop.run_until_complete(run_test())
        self.assertEqual(result, expected)

    def test_bcall_retries(self):
        attempt_count = 0

        async def retry_func(x):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Test exception")
            return x * 2

        inputs = [1, 2]
        expected = [[2, 4]]

        async def run_test():
            results = []
            async for batch_results in bcall(inputs, retry_func, 2, retries=3):
                results.append(batch_results)
            return results

        result = self.loop.run_until_complete(run_test())
        self.assertEqual(result, expected)
        self.assertEqual(attempt_count, 4)

    def test_bcall_timeout(self):
        async def timeout_func(x):
            await asyncio.sleep(1)
            return x * 2

        inputs = [1, 2]

        async def run_test():
            async for _ in bcall(inputs, timeout_func, 2, timeout=0.1):
                pass

        with self.assertRaises(asyncio.TimeoutError):
            self.loop.run_until_complete(run_test())

    def test_bcall_timing(self):
        async def delay_func(x):
            await asyncio.sleep(0.1)
            return x * 2

        inputs = [1, 2]

        async def run_test():
            results = []
            async for batch_results in bcall(inputs, delay_func, 2, timing=True):
                results.append(batch_results)
            return results

        result = self.loop.run_until_complete(run_test())
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 2)
        self.assertEqual(result[0][0][0], 2)
        self.assertIsNotNone(result[0][0][1])

    def test_bcall_concurrent_limit(self):
        start_time = self.loop.time()

        async def delay_func(x):
            await asyncio.sleep(0.1)
            return x * 2

        inputs = [1, 2, 3, 4, 5]

        async def run_test():
            async for _ in bcall(inputs, delay_func, 2, max_concurrent=2):
                pass

        self.loop.run_until_complete(run_test())
        end_time = self.loop.time()

        self.assertGreaterEqual(
            end_time - start_time, 0.3
        )  # At least 3 batches of 0.1 seconds each

    def test_bcall_throttle(self):
        start_time = self.loop.time()

        async def delay_func(x):
            await asyncio.sleep(0.1)
            return x * 2

        inputs = [1, 2, 3, 4, 5]

        async def run_test():
            async for _ in bcall(inputs, delay_func, 2, throttle_period=0.2):
                pass

        self.loop.run_until_complete(run_test())
        end_time = self.loop.time()

        self.assertGreaterEqual(
            end_time - start_time, 0.6
        )  # At least 3 throttle periods of 0.2 seconds each

    def test_bcall_initial_delay(self):
        async def delay_func(x):
            return x * 2

        inputs = [1, 2]
        start_time = self.loop.time()

        async def run_test():
            async for _ in bcall(inputs, delay_func, 2, initial_delay=0.1):
                pass

        self.loop.run_until_complete(run_test())
        end_time = self.loop.time()
        self.assertGreaterEqual(end_time - start_time, 0.1)

    def test_bcall_empty_input(self):
        inputs = []
        expected = []

        async def run_test():
            results = []
            async for batch_results in bcall(inputs, self.async_func, 2):
                results.append(batch_results)
            return results

        result = self.loop.run_until_complete(run_test())
        self.assertEqual(result, expected)

    def test_bcall_error_map(self):
        def error_handler(e):
            return str(e)

        error_map = {ValueError: error_handler}
        inputs = [1, 2, 3, 4, 5]
        expected = [
            [2, 4],
            ["Test exception", 8],
            [10],
        ]

        async def run_test():
            results = []
            async for batch_results in bcall(
                inputs, self.error_func, 2, error_map=error_map
            ):
                results.append(batch_results)
            return results

        result = self.loop.run_until_complete(run_test())
        self.assertEqual(result, expected)

    def test_bcall_async_error_map(self):
        async def async_error_handler(e):
            await asyncio.sleep(0.1)
            return str(e)

        error_map = {ValueError: async_error_handler}
        inputs = [1, 2, 3, 4, 5]
        expected = [
            [2, 4],
            ["Test exception", 8],
            [10],
        ]

        async def run_test():
            results = []
            async for batch_results in bcall(
                inputs, self.error_func, 2, error_map=error_map
            ):
                results.append(batch_results)
            return results

        result = self.loop.run_until_complete(run_test())
        self.assertEqual(result, expected)

    def test_bcall_backoff_factor(self):
        attempt_count = 0
        delays = []

        async def retry_func(x):
            nonlocal attempt_count, delays
            attempt_count += 1
            if attempt_count < 4:
                delays.append(self.loop.time())
                raise ValueError("Test exception")
            return x * 2

        inputs = [1, 2, 3]

        async def run_test():
            async for _ in bcall(
                inputs, retry_func, 2, retries=3, delay=0.1, backoff_factor=2
            ):
                pass

        self.loop.run_until_complete(run_test())
        self.assertEqual(attempt_count, 6)
        self.assertAlmostEqual(delays[2] - delays[0], 0.1, delta=0.05)

    def test_bcall_default_value(self):
        async def default_func(x):
            if x == 2:
                raise ValueError("Test exception")
            return x * 2

        inputs = [1, 2, 3, 4]
        expected = [[2, "Default"], [6, 8]]

        async def run_test():
            results = []
            async for batch_results in bcall(
                inputs, default_func, 2, default="Default"
            ):
                results.append(batch_results)
            return results

        result = self.loop.run_until_complete(run_test())
        self.assertEqual(result, expected)

    def test_bcall_kwargs(self):
        async def kwargs_func(x, y=1):
            return x * y

        inputs = [1, 2, 3, 4, 5]
        expected = [[2, 4], [6, 8], [10]]

        async def run_test():
            results = []
            async for batch_results in bcall(inputs, kwargs_func, 2, y=2):
                results.append(batch_results)
            return results

        result = self.loop.run_until_complete(run_test())
        self.assertEqual(result, expected)


import unittest


class TestLCall(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    async def async_func(self, x):
        return x * 2

    async def error_func(self, x):
        if x == 3:
            raise ValueError("Test exception")
        return x * 2

    def test_lcall_success(self):
        inputs = [1, 2, 3]
        expected = [2, 4, 6]
        result = self.loop.run_until_complete(lcall(self.async_func, inputs))
        self.assertEqual(result, expected)

    def test_lcall_with_errors(self):
        inputs = [1, 2, 3]
        expected = [2, 4, "Test exception"]

        async def mixed_func(x):
            if x == 3:
                raise ValueError("Test exception")
            return x * 2

        result = self.loop.run_until_complete(
            lcall(mixed_func, inputs, default="Test exception")
        )
        self.assertEqual(result, expected)

    def test_lcall_retries(self):
        attempt_count = 0

        async def retry_func(x):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Test exception")
            return x * 2

        inputs = [1]
        result = self.loop.run_until_complete(lcall(retry_func, inputs, retries=3))
        self.assertEqual(result, [2])
        self.assertEqual(attempt_count, 3)

    def test_lcall_timeout(self):
        async def timeout_func(x):
            await asyncio.sleep(1)
            return x * 2

        inputs = [1]
        with self.assertRaises(asyncio.TimeoutError):
            self.loop.run_until_complete(lcall(timeout_func, inputs, timeout=0.1))

    def test_lcall_timing(self):
        async def delay_func(x):
            await asyncio.sleep(0.1)
            return x * 2

        inputs = [1]
        result = self.loop.run_until_complete(lcall(delay_func, inputs, timing=True))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 2)
        self.assertIsNotNone(result[0][1])

    def test_lcall_concurrent_limit(self):
        start_time = self.loop.time()

        async def delay_func(x):
            await asyncio.sleep(0.1)
            return x * 2

        inputs = [1, 2, 3, 4, 5]
        result = self.loop.run_until_complete(
            lcall(delay_func, inputs, max_concurrent=2)
        )
        end_time = self.loop.time()

        self.assertEqual(result, [2, 4, 6, 8, 10])
        self.assertGreaterEqual(
            end_time - start_time, 0.3
        )  # At least 3 batches of 0.1 seconds each

    def test_lcall_throttle(self):
        start_time = self.loop.time()

        async def delay_func(x):
            await asyncio.sleep(0.1)
            return x * 2

        inputs = [1, 2, 3, 4, 5]
        result = self.loop.run_until_complete(
            lcall(delay_func, inputs, throttle_period=0.2)
        )
        end_time = self.loop.time()

        self.assertEqual(result, [2, 4, 6, 8, 10])
        self.assertGreaterEqual(
            end_time - start_time, 1.0
        )  # At least 5 throttle periods of 0.2 seconds each

    def test_lcall_initial_delay(self):
        async def delay_func(x):
            return x * 2

        inputs = [1]
        start_time = self.loop.time()
        result = self.loop.run_until_complete(
            lcall(delay_func, inputs, initial_delay=0.1)
        )
        end_time = self.loop.time()
        self.assertEqual(result, [2])
        self.assertGreaterEqual(end_time - start_time, 0.1)

    def test_lcall_empty_input(self):
        inputs = []
        expected = []
        result = self.loop.run_until_complete(lcall(self.async_func, inputs))
        self.assertEqual(result, expected)

    def test_lcall_error_map(self):
        def error_handler(e):
            return str(e)

        error_map = {ValueError: error_handler}
        inputs = [1, 2, 3]
        expected = [2, 4, "Test exception"]

        result = self.loop.run_until_complete(
            lcall(self.error_func, inputs, error_map=error_map)
        )
        self.assertEqual(result, expected)

    def test_lcall_async_error_map(self):
        async def async_error_handler(e):
            await asyncio.sleep(0.1)
            return str(e)

        error_map = {ValueError: async_error_handler}
        inputs = [1, 2, 3]
        expected = [2, 4, "Test exception"]

        result = self.loop.run_until_complete(
            lcall(self.error_func, inputs, error_map=error_map)
        )
        self.assertEqual(result, expected)

    def test_lcall_backoff_factor(self):
        attempt_count = 0
        delays = []

        async def retry_func(x):
            nonlocal attempt_count, delays
            attempt_count += 1
            if attempt_count < 4:
                delays.append(self.loop.time())
                raise ValueError("Test exception")
            return x * 2

        inputs = [1]
        result = self.loop.run_until_complete(
            lcall(retry_func, inputs, retries=3, delay=0.1, backoff_factor=2)
        )
        self.assertEqual(result, [2])
        self.assertEqual(attempt_count, 4)
        self.assertAlmostEqual(delays[1] - delays[0], 0.1, places=2)
        self.assertAlmostEqual(delays[2] - delays[1], 0.2, places=2)

    def test_lcall_default_value(self):
        async def default_func(x):
            if x == 2:
                raise ValueError("Test exception")
            return x * 2

        inputs = [1, 2, 3]
        expected = [2, "Default", 6]
        result = self.loop.run_until_complete(
            lcall(default_func, inputs, default="Default")
        )
        self.assertEqual(result, expected)

    def test_lcall_kwargs(self):
        async def kwargs_func(x, y=1):
            return x * y

        inputs = [1, 2, 3]
        expected = [2, 4, 6]
        result = self.loop.run_until_complete(lcall(kwargs_func, inputs, y=2))
        self.assertEqual(result, expected)


import unittest


class TestMCall(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    async def async_func(self, x):
        return x * 2

    async def another_async_func(self, x):
        return x + 3

    def test_mcall_explode(self):
        inputs = [1, 2, 3]
        funcs = [self.async_func, self.another_async_func]
        expected = [[2, 4, 6], [4, 5, 6]]

        result = self.loop.run_until_complete(mcall(inputs, funcs, explode=True))
        self.assertEqual(result, expected)

    def test_mcall_single_func(self):
        inputs = [1, 2, 3]
        func = self.async_func
        expected = [2, 4, 6]

        result = self.loop.run_until_complete(mcall(inputs, func))
        self.assertEqual(result, expected)

    def test_mcall_map(self):
        inputs = [1, 2, 3]
        funcs = [self.async_func, self.another_async_func, self.async_func]
        expected = [2, 5, 6]

        result = self.loop.run_until_complete(mcall(inputs, funcs))
        self.assertEqual(result, expected)

    def test_mcall_empty_input(self):
        inputs = []
        funcs = []
        expected = []

        result = self.loop.run_until_complete(mcall(inputs, funcs))
        self.assertEqual(result, expected)

    def test_mcall_mismatched_lengths(self):
        inputs = [1, 2, 3]
        funcs = [self.async_func, self.async_func]

        with self.assertRaises(ValueError):
            self.loop.run_until_complete(mcall(inputs, funcs))

    async def error_func(self, x):
        raise ValueError("Test exception")

    def test_mcall_with_errors(self):
        inputs = [1, 2, 3]
        funcs = [self.error_func, self.async_func, self.another_async_func]
        expected = ["Default", 4, 6]

        async def error_handler(e):
            return str(e)

        error_map = {ValueError: error_handler}
        result = self.loop.run_until_complete(
            mcall(inputs, funcs, error_map=error_map, default="Default")
        )
        self.assertEqual(result, expected)

    def test_mcall_kwargs(self):
        async def kwargs_func(x, y=1):
            return x * y

        inputs = [1, 2, 3]
        func = kwargs_func
        expected = [2, 4, 6]

        result = self.loop.run_until_complete(mcall(inputs, func, y=2))
        self.assertEqual(result, expected)

    def test_mcall_single_func_with_errors(self):
        inputs = [1, 2, 3]
        func = self.error_func
        expected = ["Default", "Default", "Default"]

        result = self.loop.run_until_complete(mcall(inputs, func, default="Default"))
        self.assertEqual(result, expected)

    def test_mcall_single_func_with_custom_error_map(self):
        async def custom_error_func(x):
            if x == 2:
                raise ValueError("Custom error")
            return x * 2

        async def custom_error_handler(e):
            return f"Handled {str(e)}"

        inputs = [1, 2, 3]
        func = custom_error_func
        expected = [2, "Handled Custom error", 6]

        error_map = {ValueError: custom_error_handler}
        result = self.loop.run_until_complete(mcall(inputs, func, error_map=error_map))
        self.assertEqual(result, expected)

    def test_mcall_explode_with_single_function(self):
        inputs = [1, 2, 3]
        funcs = [self.async_func]
        expected = [[2, 4, 6]]

        result = self.loop.run_until_complete(mcall(inputs, funcs, explode=True))
        self.assertEqual(result, expected)

    def test_mcall_with_long_running_tasks(self):
        async def long_running_func(x):
            await asyncio.sleep(0.5)
            return x * 2

        inputs = [1, 2, 3]
        func = long_running_func
        expected = [2, 4, 6]

        result = self.loop.run_until_complete(mcall(inputs, func))
        self.assertEqual(result, expected)

    def test_mcall_with_different_types_of_inputs(self):
        async def string_func(x):
            return x.upper()

        async def int_func(x):
            return x * 2

        inputs = ["a", 1, "b", 2]
        funcs = [string_func, int_func, string_func, int_func]
        expected = ["A", 2, "B", 4]

        result = self.loop.run_until_complete(mcall(inputs, funcs))
        self.assertEqual(result, expected)

    def test_mcall_with_async_context_manager(self):
        class AsyncContextManager:
            def __init__(self, value):
                self.value = value

            async def __aenter__(self):
                return self.value * 2

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        async def async_context_func(x):
            async with AsyncContextManager(x) as result:
                return result

        inputs = [1, 2, 3]
        func = async_context_func
        expected = [2, 4, 6]

        result = self.loop.run_until_complete(mcall(inputs, func))
        self.assertEqual(result, expected)

    def test_mcall_with_nested_async_functions(self):
        async def nested_async_func(x):
            async def inner_func(y):
                return y * 2

            return await inner_func(x)

        inputs = [1, 2, 3]
        func = nested_async_func
        expected = [2, 4, 6]

        result = self.loop.run_until_complete(mcall(inputs, func))
        self.assertEqual(result, expected)

    def test_mcall_with_async_lambda(self):
        async_lambda = lambda x: x * 2

        inputs = [1, 2, 3]
        func = async_lambda
        expected = [2, 4, 6]

        result = self.loop.run_until_complete(mcall(inputs, func))
        self.assertEqual(result, expected)

    def test_mcall_with_coroutine_function(self):
        async def coroutine_func(x):
            await asyncio.sleep(0.1)
            return x * 2

        inputs = [1, 2, 3]
        func = coroutine_func
        expected = [2, 4, 6]

        result = self.loop.run_until_complete(mcall(inputs, func))
        self.assertEqual(result, expected)

    def test_mcall_with_async_list_comprehension(self):
        async def list_comprehension_func(x):
            return [await asyncio.sleep(0.1) or i * 2 for i in range(x)]

        inputs = [1, 2, 3]
        func = list_comprehension_func
        expected = [[0], [0, 2], [0, 2, 4]]

        result = self.loop.run_until_complete(mcall(inputs, func))
        self.assertEqual(result, expected)

    def test_mcall_with_async_dict_comprehension(self):
        async def dict_comprehension_func(x):
            return {i: await asyncio.sleep(0.1) or i * 2 for i in range(x)}

        inputs = [1, 2, 3]
        func = dict_comprehension_func
        expected = [{0: 0}, {0: 0, 1: 2}, {0: 0, 1: 2, 2: 4}]

        result = self.loop.run_until_complete(mcall(inputs, func))
        self.assertEqual(result, expected)

    def test_mcall_with_async_set_comprehension(self):
        async def set_comprehension_func(x):
            return {await asyncio.sleep(0.1) or i * 2 for i in range(x)}

        inputs = [1, 2, 3]
        func = set_comprehension_func
        expected = [{0}, {0, 2}, {0, 2, 4}]

        result = self.loop.run_until_complete(mcall(inputs, func))
        self.assertEqual(result, expected)

    def test_mcall_with_async_error_handling(self):
        async def async_error_func(x):
            if x == 2:
                raise ValueError("Async error")
            return x * 2

        async def async_error_handler(e):
            return f"Async handled {str(e)}"

        inputs = [1, 2, 3]
        func = async_error_func
        expected = [2, "Async handled Async error", 6]

        error_map = {ValueError: async_error_handler}
        result = self.loop.run_until_complete(mcall(inputs, func, error_map=error_map))
        self.assertEqual(result, expected)


class TestPCall(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    async def async_func1(self):
        return "func1"

    async def async_func2(self):
        return "func2"

    async def error_func(self):
        raise ValueError("Test exception")

    def test_pcall_success(self):
        funcs = [self.async_func1, self.async_func2]
        expected = ["func1", "func2"]
        result = self.loop.run_until_complete(pcall(funcs))
        self.assertEqual(result, expected)

    def test_pcall_with_errors(self):
        funcs = [self.async_func1, self.error_func]
        expected = ["func1", "Test exception"]

        result = self.loop.run_until_complete(pcall(funcs, default="Test exception"))
        self.assertEqual(result, expected)

    def test_pcall_retries(self):
        attempt_count = 0

        async def retry_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Test exception")
            return "success"

        funcs = [retry_func]
        result = self.loop.run_until_complete(pcall(funcs, retries=3))
        self.assertEqual(result, ["success"])
        self.assertEqual(attempt_count, 3)

    def test_pcall_timeout(self):
        async def timeout_func():
            await asyncio.sleep(1)
            return "timeout"

        funcs = [timeout_func]
        with self.assertRaises(asyncio.TimeoutError):
            self.loop.run_until_complete(pcall(funcs, timeout=0.1))

    def test_pcall_timing(self):
        async def delay_func():
            await asyncio.sleep(0.1)
            return "delay"

        funcs = [delay_func]
        result = self.loop.run_until_complete(pcall(funcs, timing=True))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "delay")
        self.assertIsNotNone(result[0][1])

    def test_pcall_concurrent_limit(self):
        start_time = self.loop.time()

        async def delay_func():
            await asyncio.sleep(0.1)
            return "delay"

        funcs = [delay_func] * 5
        self.loop.run_until_complete(pcall(funcs, max_concurrent=2))
        end_time = self.loop.time()

        self.assertGreaterEqual(
            end_time - start_time, 0.3
        )  # At least 3 batches of 0.1 seconds each

    def test_pcall_throttle(self):
        start_time = self.loop.time()

        async def delay_func():
            await asyncio.sleep(0.1)
            return "delay"

        funcs = [delay_func] * 5
        self.loop.run_until_complete(pcall(funcs, throttle_period=0.2))
        end_time = self.loop.time()

        self.assertGreaterEqual(
            end_time - start_time, 1.0
        )  # At least 5 throttle periods of 0.2 seconds each

    def test_pcall_initial_delay(self):
        async def delay_func():
            return "delay"

        funcs = [delay_func]
        start_time = self.loop.time()
        self.loop.run_until_complete(pcall(funcs, initial_delay=0.1))
        end_time = self.loop.time()
        self.assertGreaterEqual(end_time - start_time, 0.1)

    def test_pcall_empty_funcs(self):
        funcs = []
        expected = []
        result = self.loop.run_until_complete(pcall(funcs))
        self.assertEqual(result, expected)

    def test_pcall_error_map(self):
        def error_handler(e):
            return str(e)

        error_map = {ValueError: error_handler}
        funcs = [self.async_func1, self.error_func]
        expected = ["func1", "Test exception"]

        result = self.loop.run_until_complete(pcall(funcs, error_map=error_map))
        self.assertEqual(result, expected)

    def test_pcall_async_error_map(self):
        async def async_error_handler(e):
            await asyncio.sleep(0.1)
            return str(e)

        error_map = {ValueError: async_error_handler}
        funcs = [self.async_func1, self.error_func]
        expected = ["func1", "Test exception"]

        result = self.loop.run_until_complete(pcall(funcs, error_map=error_map))
        self.assertEqual(result, expected)

    def test_pcall_backoff_factor(self):
        attempt_count = 0
        delays = []

        async def retry_func():
            nonlocal attempt_count, delays
            attempt_count += 1
            if attempt_count < 4:
                delays.append(self.loop.time())
                raise ValueError("Test exception")
            return "success"

        funcs = [retry_func]
        result = self.loop.run_until_complete(
            pcall(funcs, retries=3, delay=0.1, backoff_factor=2)
        )
        self.assertEqual(result, ["success"])
        self.assertEqual(attempt_count, 4)
        self.assertAlmostEqual(delays[1] - delays[0], 0.1, places=2)
        self.assertAlmostEqual(delays[2] - delays[1], 0.2, places=2)

    def test_pcall_default_value(self):
        async def default_func():
            raise ValueError("Test exception")

        funcs = [self.async_func1, default_func]
        expected = ["func1", "Default"]
        result = self.loop.run_until_complete(pcall(funcs, default="Default"))
        self.assertEqual(result, expected)

    def test_pcall_kwargs(self):
        async def kwargs_func(x=1):
            return x

        funcs = [kwargs_func]
        expected = [2]
        result = self.loop.run_until_complete(pcall(funcs, x=2))
        self.assertEqual(result, expected)


class TestRCall(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    async def async_func(self, x):
        return x * 2

    def test_rcall_success(self):
        result = self.loop.run_until_complete(rcall(self.async_func, 2))
        self.assertEqual(result, 4)

    def test_rcall_failure(self):
        async def error_func():
            raise ValueError("Test exception")

        with self.assertRaises(RuntimeError) as context:
            self.loop.run_until_complete(rcall(error_func))
        self.assertIn("Test exception", str(context.exception))

    def test_rcall_retries(self):
        attempt_count = 0

        async def retry_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Test exception")
            return 42

        result = self.loop.run_until_complete(rcall(retry_func, retries=3))
        self.assertEqual(result, 42)
        self.assertEqual(attempt_count, 3)

    def test_rcall_default_value(self):
        async def error_func():
            raise ValueError("Test exception")

        result = self.loop.run_until_complete(rcall(error_func, default=99))
        self.assertEqual(result, 99)

    def test_rcall_timing(self):
        async def delay_func():
            await asyncio.sleep(0.1)
            return 42

        result, duration = self.loop.run_until_complete(rcall(delay_func, timing=True))
        self.assertEqual(result, 42)
        self.assertGreaterEqual(duration, 0.1)

    def test_rcall_timeout(self):
        async def timeout_func():
            await asyncio.sleep(1)

        with self.assertRaises(RuntimeError) as context:
            self.loop.run_until_complete(rcall(timeout_func, timeout=0.1))
        self.assertIn("Timeout", str(context.exception))

    def test_rcall_error_map(self):
        def handle_value_error(e):
            self.error_handled = True

        self.error_handled = False

        async def error_func():
            raise ValueError("Test exception")

        self.loop.run_until_complete(
            rcall(error_func, error_map={ValueError: handle_value_error})
        )
        self.assertTrue(self.error_handled)

    def test_rcall_verbose(self):
        attempt_count = 0

        async def retry_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Test exception")
            return 42

        with patch("builtins.print") as mock_print:
            result = self.loop.run_until_complete(
                rcall(retry_func, retries=3, verbose=True)
            )
            self.assertEqual(result, 42)
            self.assertEqual(attempt_count, 3)
            mock_print.assert_any_call(
                "Attempt 1/4 failed: Test exception, retrying..."
            )
            mock_print.assert_any_call(
                "Attempt 2/4 failed: Test exception, retrying..."
            )

    def test_rcall_custom_error_message(self):
        async def error_func():
            raise ValueError("Test exception")

        with self.assertRaises(RuntimeError) as context:
            self.loop.run_until_complete(rcall(error_func, error_msg="Custom error"))
        self.assertIn("Custom error", str(context.exception))

    def test_rcall_initial_delay(self):
        start_time = self.loop.time()

        async def delay_func():
            return 42

        result = self.loop.run_until_complete(rcall(delay_func, initial_delay=0.1))
        end_time = self.loop.time()
        self.assertEqual(result, 42)
        self.assertGreaterEqual(end_time - start_time, 0.1)

    def test_rcall_backoff_factor(self):
        attempt_count = 0
        delays = []

        async def retry_func():
            nonlocal attempt_count, delays
            attempt_count += 1
            delays.append(self.loop.time())
            if attempt_count < 3:
                raise ValueError("Test exception")
            return 42

        with patch("builtins.print"):
            result = self.loop.run_until_complete(
                rcall(retry_func, retries=3, delay=0.1, backoff_factor=2)
            )
            self.assertEqual(result, 42)
            self.assertEqual(attempt_count, 3)
            self.assertAlmostEqual(delays[1] - delays[0], 0.1, places=1)
            self.assertAlmostEqual(delays[2] - delays[1], 0.2, places=1)

    def test_rcall_multiple_exceptions(self):
        async def error_func():
            if self.loop.time() % 2 == 0:
                raise ValueError("Test ValueError")
            else:
                raise KeyError("Test KeyError")

        def handle_value_error(e):
            self.value_error_handled = True

        def handle_key_error(e):
            self.key_error_handled = True

        self.value_error_handled = False
        self.key_error_handled = False

        self.loop.run_until_complete(
            rcall(
                error_func,
                retries=2,
                error_map={ValueError: handle_value_error, KeyError: handle_key_error},
            )
        )
        self.assertTrue(self.value_error_handled or self.key_error_handled)

    def test_rcall_no_retries(self):
        attempt_count = 0

        async def no_retry_func():
            nonlocal attempt_count
            attempt_count += 1
            raise ValueError("Test exception")

        with self.assertRaises(RuntimeError) as context:
            self.loop.run_until_complete(rcall(no_retry_func, retries=0))
        self.assertEqual(attempt_count, 1)
        self.assertIn("Test exception", str(context.exception))

    def test_rcall_multiple_default_values(self):
        async def error_func():
            raise ValueError("Test exception")

        result1 = self.loop.run_until_complete(rcall(error_func, default=99))
        result2 = self.loop.run_until_complete(rcall(error_func, default=100))
        self.assertEqual(result1, 99)
        self.assertEqual(result2, 100)

    def test_rcall_ignore_error(self):
        async def error_func():
            raise ValueError("Test exception")

        result = self.loop.run_until_complete(
            rcall(error_func, default=99, timing=True)
        )
        self.assertEqual(result, 99)

    def test_rcall_with_kwargs(self):
        async def add_func(x, y):
            return x + y

        result = self.loop.run_until_complete(rcall(add_func, x=3, y=4))
        self.assertEqual(result, 7)

    def test_rcall_multiple_exceptions(self):
        async def error_func():
            if self.loop.time() % 2 == 0:
                raise ValueError("Test ValueError")
            else:
                raise KeyError("Test KeyError")

        def handle_value_error(e):
            self.value_error_handled = True

        def handle_key_error(e):
            self.key_error_handled = True

        self.value_error_handled = False
        self.key_error_handled = False

        self.loop.run_until_complete(
            rcall(
                error_func,
                retries=2,
                error_map={ValueError: handle_value_error, KeyError: handle_key_error},
            )
        )
        self.assertTrue(self.value_error_handled or self.key_error_handled)

    def test_rcall_no_retries(self):
        attempt_count = 0

        async def no_retry_func():
            nonlocal attempt_count
            attempt_count += 1
            raise ValueError("Test exception")

        with self.assertRaises(RuntimeError) as context:
            self.loop.run_until_complete(rcall(no_retry_func, retries=0))
        self.assertEqual(attempt_count, 1)
        self.assertIn("Test exception", str(context.exception))

    def test_rcall_multiple_default_values(self):
        async def error_func():
            raise ValueError("Test exception")

        result1 = self.loop.run_until_complete(rcall(error_func, default=99))
        result2 = self.loop.run_until_complete(rcall(error_func, default=100))
        self.assertEqual(result1, 99)
        self.assertEqual(result2, 100)

    def test_rcall_ignore_error(self):
        async def error_func():
            raise ValueError("Test exception")

        result = self.loop.run_until_complete(
            rcall(error_func, default=99, timing=True)
        )
        self.assertEqual(result, 99)

    def test_rcall_with_kwargs(self):
        async def add_func(x, y):
            return x + y

        result = self.loop.run_until_complete(rcall(add_func, x=3, y=4))
        self.assertEqual(result, 7)

    def test_rcall_complex_backoff(self):
        attempt_count = 0
        delays = []

        async def retry_func():
            nonlocal attempt_count, delays
            attempt_count += 1
            delays.append(self.loop.time())
            if attempt_count < 4:
                raise ValueError("Test exception")
            return 42

        with patch("builtins.print"):
            result = self.loop.run_until_complete(
                rcall(retry_func, retries=4, delay=0.1, backoff_factor=3)
            )
            self.assertEqual(result, 42)
            self.assertEqual(attempt_count, 4)
            self.assertAlmostEqual(delays[1] - delays[0], 0.1, places=1)
            self.assertAlmostEqual(delays[2] - delays[1], 0.3, places=1)
            self.assertAlmostEqual(delays[3] - delays[2], 0.9, places=1)

    def test_rcall_exponential_backoff(self):
        attempt_count = 0

        async def retry_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 4:
                raise ValueError("Test exception")
            return 42

        with patch("builtins.print"):
            result = self.loop.run_until_complete(
                rcall(retry_func, retries=3, delay=0.1, backoff_factor=2)
            )
            self.assertEqual(result, 42)
            self.assertEqual(attempt_count, 4)

    def test_rcall_error_map_with_default(self):
        def handle_value_error(e):
            self.value_error_handled = True

        self.value_error_handled = False

        async def error_func():
            raise ValueError("Test exception")

        result = self.loop.run_until_complete(
            rcall(
                error_func,
                retries=2,
                error_map={ValueError: handle_value_error},
                default=99,
            )
        )
        self.assertEqual(result, 99)
        self.assertTrue(self.value_error_handled)

    def test_rcall_timeout_with_default(self):
        async def timeout_func():
            await asyncio.sleep(1)

        result = self.loop.run_until_complete(
            rcall(timeout_func, timeout=0.1, default=99)
        )
        self.assertEqual(result, 99)


# Mock functions for testing
async def async_func(x):
    await asyncio.sleep(0.1)
    return x * 2


def sync_func(x):
    return x * 2


async def error_func():
    raise ValueError("Test exception")


class TestTcall(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        pending_tasks = [
            task for task in asyncio.all_tasks(loop=self.loop) if not task.done()
        ]
        if pending_tasks:
            self.loop.run_until_complete(
                asyncio.gather(*pending_tasks, return_exceptions=True)
            )
        self.loop.close()

    def test_tcall_with_async_func(self):
        result = self.loop.run_until_complete(tcall(async_func, 2))
        self.assertEqual(result, 4)

    def test_tcall_with_sync_func(self):
        result = self.loop.run_until_complete(tcall(sync_func, 2))
        self.assertEqual(result, 4)

    def test_tcall_with_initial_delay(self):
        start_time = self.loop.time()
        result = self.loop.run_until_complete(tcall(async_func, 2, initial_delay=1))
        end_time = self.loop.time()
        self.assertEqual(result, 4)
        self.assertAlmostEqual(
            end_time - start_time, 1.1, delta=0.1
        )  # Adjusted to 1.1 to account for function execution time

    def test_tcall_with_timeout(self):
        with self.assertRaises(asyncio.TimeoutError):
            self.loop.run_until_complete(tcall(async_func, 2, timeout=0.05))

    def test_tcall_with_suppress_err(self):
        result = self.loop.run_until_complete(
            tcall(error_func, suppress_err=True, default="default")
        )
        self.assertEqual(result, "default")

    def test_tcall_with_timing(self):
        result, duration = self.loop.run_until_complete(
            tcall(async_func, 2, timing=True)
        )
        self.assertEqual(result, 4)
        self.assertAlmostEqual(duration, 0.1, delta=0.05)

    def test_tcall_with_custom_error_message(self):
        with self.assertRaises(RuntimeError) as context:
            self.loop.run_until_complete(
                tcall(error_func, error_msg="Custom error message")
            )
        self.assertIn("Custom error message", str(context.exception))

    def test_tcall_with_timeout_and_suppress_err(self):
        result = self.loop.run_until_complete(
            tcall(async_func, 2, timeout=0.05, suppress_err=True, default="default")
        )
        self.assertEqual(result, "default")

    def test_tcall_with_timeout_timing_and_suppress_err(self):
        result, duration = self.loop.run_until_complete(
            tcall(
                async_func,
                2,
                timeout=0.05,
                suppress_err=True,
                default="default",
                timing=True,
            )
        )
        self.assertEqual(result, "default")
        self.assertAlmostEqual(duration, 0.05, delta=0.05)

    def test_tcall_with_error_map_async(self):
        def handle_value_error(e):
            self.error_handled = True

        self.error_handled = False
        result = self.loop.run_until_complete(
            tcall(error_func, error_map={ValueError: handle_value_error}, timing=True)
        )
        self.assertIsNone(result[0])
        self.assertTrue(self.error_handled)

    def test_tcall_with_error_map_sync(self):
        def handle_value_error(e):
            self.error_handled = True

        def sync_error_func():
            raise ValueError("Test exception")

        self.error_handled = False
        result = self.loop.run_until_complete(
            tcall(
                sync_error_func, error_map={ValueError: handle_value_error}, timing=True
            )
        )
        self.assertIsNone(result[0])
        self.assertTrue(self.error_handled)

    def test_tcall_with_sync_func_timeout(self):
        def sync_sleep_func():
            time.sleep(0.1)
            return 42

        with self.assertRaises(asyncio.TimeoutError):
            self.loop.run_until_complete(tcall(sync_sleep_func, timeout=0.05))

    def test_tcall_with_sync_func_timeout_suppress_err(self):
        def sync_sleep_func():
            time.sleep(0.1)
            return 42

        result = self.loop.run_until_complete(
            tcall(sync_sleep_func, timeout=0.05, suppress_err=True, default="default")
        )
        self.assertEqual(result, "default")

    def test_tcall_with_kwargs(self):
        async def async_func_with_kwargs(x, y=10):
            await asyncio.sleep(0.1)
            return x + y

        result = self.loop.run_until_complete(tcall(async_func_with_kwargs, 5, y=20))
        self.assertEqual(result, 25)

    def test_tcall_with_sync_func_kwargs(self):
        def sync_func_with_kwargs(x, y=10):
            return x + y

        result = self.loop.run_until_complete(tcall(sync_func_with_kwargs, 5, y=20))
        self.assertEqual(result, 25)

    def test_tcall_with_zero_timeout(self):
        with self.assertRaises(asyncio.TimeoutError):
            self.loop.run_until_complete(tcall(async_func, 2, timeout=0))

    def test_tcall_with_negative_timeout(self):
        with self.assertRaises(asyncio.TimeoutError):
            self.loop.run_until_complete(tcall(async_func, 2, timeout=-1))

    def test_tcall_with_sync_func_error(self):
        def sync_error_func():
            raise ValueError("Test exception")

        with self.assertRaises(RuntimeError) as context:
            self.loop.run_until_complete(tcall(sync_error_func))
        self.assertIn("An error occurred in async execution", str(context.exception))

    def test_tcall_with_sync_func_error_suppress(self):
        def sync_error_func():
            raise ValueError("Test exception")

        result = self.loop.run_until_complete(
            tcall(sync_error_func, suppress_err=True, default="default")
        )
        self.assertEqual(result, "default")


class TestThrottle(unittest.TestCase):

    def test_synchronous_throttling(self):
        call_times = [0, 0, 1, 1]

        def mock_get_now(datetime_=False):
            return call_times.pop(0)

        def mock_sleep(duration):
            pass

        throttled_func = Throttle(1)(lambda: "result")
        throttled_func.last_called = mock_get_now()

        result1 = throttled_func()
        throttled_func.last_called = mock_get_now()
        result2 = throttled_func()

        self.assertEqual(result1, "result")
        self.assertEqual(result2, "result")

    async def test_asynchronous_throttling(self):
        call_times = [0, 0, 1, 1]

        def mock_get_now(datetime_=False):
            return call_times.pop(0)

        async def mock_sleep(duration):
            pass

        async def async_func():
            return "result"

        throttled_func = Throttle(1).__call_async__(async_func)
        throttled_func.last_called = mock_get_now()

        result1 = await throttled_func()
        throttled_func.last_called = mock_get_now()
        result2 = await throttled_func()

        self.assertEqual(result1, "result")
        self.assertEqual(result2, "result")

    def test_no_throttling_needed_sync(self):
        call_times = [0, 1, 2, 3]

        def mock_get_now(datetime_=False):
            return call_times.pop(0)

        throttled_func = Throttle(1)(lambda: "result")
        throttled_func.last_called = mock_get_now()

        result1 = throttled_func()
        throttled_func.last_called = mock_get_now()
        result2 = throttled_func()

        self.assertEqual(result1, "result")
        self.assertEqual(result2, "result")

    async def test_no_throttling_needed_async(self):
        call_times = [0, 1, 2, 3]

        def mock_get_now(datetime_=False):
            return call_times.pop(0)

        async def async_func():
            return "result"

        throttled_func = Throttle(1).__call_async__(async_func)
        throttled_func.last_called = mock_get_now()

        result1 = await throttled_func()
        throttled_func.last_called = mock_get_now()
        result2 = await throttled_func()

        self.assertEqual(result1, "result")
        self.assertEqual(result2, "result")

    def test_edge_case_sync(self):
        call_times = [0, 0.5, 1, 1.5]

        def mock_get_now(datetime_=False):
            return call_times.pop(0)

        throttled_func = Throttle(1)(lambda: "result")
        throttled_func.last_called = mock_get_now()

        result1 = throttled_func()
        throttled_func.last_called = mock_get_now()
        result2 = throttled_func()

        self.assertEqual(result1, "result")
        self.assertEqual(result2, "result")

    async def test_edge_case_async(self):
        call_times = [0, 0.5, 1, 1.5]

        def mock_get_now(datetime_=False):
            return call_times.pop(0)

        async def async_func():
            return "result"

        throttled_func = Throttle(1).__call_async__(async_func)
        throttled_func.last_called = mock_get_now()

        result1 = await throttled_func()
        throttled_func.last_called = mock_get_now()
        result2 = await throttled_func()

        self.assertEqual(result1, "result")
        self.assertEqual(result2, "result")

    async def test_asynchronous_throttling(self):
        call_times = [0, 0, 1, 1]

        def mock_get_now(datetime_=False):
            return call_times.pop(0)

        async def async_func():
            return "result"

        throttled_func = Throttle(1).__call_async__(async_func)
        throttled_func.last_called = mock_get_now()

        result1 = await throttled_func()
        throttled_func.last_called = mock_get_now()
        result2 = await throttled_func()

        self.assertEqual(result1, "result")
        self.assertEqual(result2, "result")

    async def test_no_throttling_needed_async(self):
        call_times = [0, 1, 2, 3]

        def mock_get_now(datetime_=False):
            return call_times.pop(0)

        async def async_func():
            return "result"

        throttled_func = Throttle(1).__call_async__(async_func)
        throttled_func.last_called = mock_get_now()

        result1 = await throttled_func()
        throttled_func.last_called = mock_get_now()
        result2 = await throttled_func()

        self.assertEqual(result1, "result")
        self.assertEqual(result2, "result")

    async def test_edge_case_async(self):
        call_times = [0, 0.5, 1, 1.5]

        def mock_get_now(datetime_=False):
            return call_times.pop(0)

        async def async_func():
            return "result"

        throttled_func = Throttle(1).__call_async__(async_func)
        throttled_func.last_called = mock_get_now()

        result1 = await throttled_func()
        throttled_func.last_called = mock_get_now()
        result2 = await throttled_func()

        self.assertEqual(result1, "result")
        self.assertEqual(result2, "result")

    async def test_multiple_async_throttled_funcs(self):
        call_times = [0, 0, 1, 1, 2, 2, 3, 3]

        def mock_get_now(datetime_=False):
            return call_times.pop(0)

        async def async_func_1():
            return "result1"

        async def async_func_2():
            return "result2"

        throttled_func_1 = Throttle(1).__call_async__(async_func_1)
        throttled_func_2 = Throttle(1).__call_async__(async_func_2)
        throttled_func_1.last_called = mock_get_now()
        throttled_func_2.last_called = mock_get_now()

        result1 = await throttled_func_1()
        throttled_func_1.last_called = mock_get_now()
        result2 = await throttled_func_1()

        result3 = await throttled_func_2()
        throttled_func_2.last_called = mock_get_now()
        result4 = await throttled_func_2()

        self.assertEqual(result1, "result1")
        self.assertEqual(result2, "result1")
        self.assertEqual(result3, "result2")
        self.assertEqual(result4, "result2")


class TestUcall(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    async def async_func(self, x):
        return x * 2

    def sync_func(self, x):
        return x * 2

    def test_ucall_with_async_func(self):
        result = self.loop.run_until_complete(ucall(self.async_func, 2))
        self.assertEqual(result, 4)

    def test_ucall_with_async_func_and_kwargs(self):
        async def async_func_with_kwargs(x, y=1):
            return x * y

        result = self.loop.run_until_complete(ucall(async_func_with_kwargs, 2, y=3))
        self.assertEqual(result, 6)

    def test_ucall_with_sync_func(self):
        result = self.loop.run_until_complete(ucall(self.sync_func, 2))
        self.assertEqual(result, 4)

    def test_ucall_with_sync_func_and_kwargs(self):
        def sync_func_with_kwargs(x, y=1):
            return x * y

        result = self.loop.run_until_complete(ucall(sync_func_with_kwargs, 2, y=3))
        self.assertEqual(result, 6)

    def test_ucall_with_error_handling(self):
        def handle_value_error(e):
            self.error_handled = True

        self.error_handled = False

        async def error_func():
            raise ValueError("Test exception")

        with self.assertRaises(ValueError):
            self.loop.run_until_complete(
                ucall(error_func, error_map={ValueError: handle_value_error})
            )

        self.assertTrue(self.error_handled)

    def test_ucall_with_no_running_loop(self):
        result = self.loop.run_until_complete(ucall(self.async_func, 2))
        self.assertEqual(result, 4)

    def test_ucall_with_runtime_error(self):
        with patch("asyncio.get_running_loop", side_effect=RuntimeError):
            result = self.loop.run_until_complete(ucall(self.async_func, 2))
            self.assertEqual(result, 4)

    def test_ucall_sync_func_with_error_handling(self):
        def handle_value_error(e):
            self.error_handled = True

        self.error_handled = False

        def error_func():
            raise ValueError("Test exception")

        with self.assertRaises(ValueError):
            self.loop.run_until_complete(
                ucall(error_func, error_map={ValueError: handle_value_error})
            )

        self.assertTrue(self.error_handled)

    def test_ucall_with_different_exception(self):
        def handle_type_error(e):
            self.error_handled = True

        self.error_handled = False

        async def error_func():
            raise TypeError("Test exception")

        with self.assertRaises(TypeError):
            self.loop.run_until_complete(
                ucall(error_func, error_map={TypeError: handle_type_error})
            )

        self.assertTrue(self.error_handled)

    def test_ucall_without_error_map(self):
        async def error_func():
            raise ValueError("Test exception")

        with self.assertRaises(ValueError):
            self.loop.run_until_complete(ucall(error_func))

    def test_ucall_nested_async_calls(self):
        async def nested_async_func(x):
            return await self.async_func(x) + 1

        result = self.loop.run_until_complete(ucall(nested_async_func, 2))
        self.assertEqual(result, 5)

    def test_ucall_sync_func_raising_exception(self):
        def handle_exception(e):
            self.error_handled = True

        self.error_handled = False

        def error_func():
            raise Exception("Test exception")

        with self.assertRaises(Exception):
            self.loop.run_until_complete(
                ucall(error_func, error_map={Exception: handle_exception})
            )

        self.assertTrue(self.error_handled)

    def test_ucall_with_args_and_kwargs(self):
        async def async_func_with_args(x, y, z=1):
            return x + y + z

        result = self.loop.run_until_complete(ucall(async_func_with_args, 1, 2, z=3))
        self.assertEqual(result, 6)

    def test_ucall_with_async_generator(self):
        async def async_generator(x):
            for i in range(x):
                yield i

        async def async_func_with_generator(x):
            result = 0
            async for i in async_generator(x):
                result += i
            return result

        result = self.loop.run_until_complete(ucall(async_func_with_generator, 3))
        self.assertEqual(result, 3)

    def test_ucall_with_async_context_manager(self):
        class AsyncContextManager:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        async def async_func_with_context_manager():
            async with AsyncContextManager():
                return 42

        result = self.loop.run_until_complete(ucall(async_func_with_context_manager))
        self.assertEqual(result, 42)

    def test_ucall_with_async_generator_and_error_handling(self):
        def handle_exception(e):
            self.error_handled = True

        self.error_handled = False

        async def async_generator_with_error(x):
            for i in range(x):
                if i == 1:
                    raise ValueError("Test exception")
                yield i

        async def async_func_with_error_generator(x):
            result = 0
            async for i in async_generator_with_error(x):
                result += i
            return result

        with self.assertRaises(ValueError):
            self.loop.run_until_complete(
                ucall(
                    async_func_with_error_generator,
                    3,
                    error_map={ValueError: handle_exception},
                )
            )

        self.assertTrue(self.error_handled)

    def test_ucall_with_async_context_manager_and_error_handling(self):
        def handle_exception(e):
            self.error_handled = True

        self.error_handled = False

        class AsyncContextManagerWithError:
            async def __aenter__(self):
                raise ValueError("Test exception")

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        async def async_func_with_error_context_manager():
            async with AsyncContextManagerWithError():
                return 42

        with self.assertRaises(ValueError):
            self.loop.run_until_complete(
                ucall(
                    async_func_with_error_context_manager,
                    error_map={ValueError: handle_exception},
                )
            )

        self.assertTrue(self.error_handled)

    def test_ucall_with_multiple_error_handlers(self):
        def handle_value_error(e):
            self.value_error_handled = True

        def handle_type_error(e):
            self.type_error_handled = True

        self.value_error_handled = False
        self.type_error_handled = False

        async def error_func():
            raise ValueError("Test exception")

        with self.assertRaises(ValueError):
            self.loop.run_until_complete(
                ucall(
                    error_func,
                    error_map={
                        ValueError: handle_value_error,
                        TypeError: handle_type_error,
                    },
                )
            )

        self.assertTrue(self.value_error_handled)
        self.assertFalse(self.type_error_handled)

    def test_ucall_with_async_func_returning_none(self):
        async def async_func_returning_none():
            return None

        result = self.loop.run_until_complete(ucall(async_func_returning_none))
        self.assertIsNone(result)

    def test_ucall_with_sync_func_returning_none(self):
        def sync_func_returning_none():
            return None

        result = self.loop.run_until_complete(ucall(sync_func_returning_none))
        self.assertIsNone(result)

    def test_ucall_with_async_func_raising_exception(self):
        async def async_func_raising_exception():
            raise Exception("Test exception")

        with self.assertRaises(Exception):
            self.loop.run_until_complete(ucall(async_func_raising_exception))

    def test_ucall_with_sync_func_raising_exception(self):
        def sync_func_raising_exception():
            raise Exception("Test exception")

        with self.assertRaises(Exception):
            self.loop.run_until_complete(ucall(sync_func_raising_exception))

    def test_ucall_with_async_func_and_args(self):
        async def async_func_with_args(x, y):
            return x + y

        result = self.loop.run_until_complete(ucall(async_func_with_args, 2, 3))
        self.assertEqual(result, 5)

    def test_ucall_with_sync_func_and_args(self):
        def sync_func_with_args(x, y):
            return x + y

        result = self.loop.run_until_complete(ucall(sync_func_with_args, 2, 3))
        self.assertEqual(result, 5)


class TestFunctionModule(unittest.TestCase):

    async def test_force_async(self):
        def sync_func(x):
            return x * 2

        async_func = force_async(sync_func)
        result = await async_func(2)
        self.assertEqual(result, 4)

    # def test_force_async_multiple_calls(self):
    #     def sync_func(x):
    #         return x * 2

    #     async_func = force_async(sync_func)

    #     loop = asyncio.get_event_loop()
    #     results = loop.run_until_complete(asyncio.gather(async_func(2), async_func(3)))
    #     self.assertEqual(results, [4, 6])

    def test_force_async_with_exceptions(self):
        def sync_func(x):
            raise ValueError("Test exception")

        async_func = force_async(sync_func)

        loop = asyncio.get_event_loop()
        with self.assertRaises(ValueError):
            loop.run_until_complete(async_func(2))

    def test_is_coroutine_func_with_async(self):
        async def async_func():
            pass

        self.assertTrue(is_coroutine_func(async_func))

    def test_is_coroutine_func_with_sync(self):
        def sync_func():
            pass

        self.assertFalse(is_coroutine_func(sync_func))

    def test_is_coroutine_func_cached(self):
        async def async_func():
            pass

        self.assertTrue(is_coroutine_func(async_func))
        self.assertTrue(is_coroutine_func(async_func))

    def test_custom_error_handler_with_known_error(self):
        def handle_value_error(e):
            self.error_handled = True

        self.error_handled = False
        custom_error_handler(ValueError(), {ValueError: handle_value_error})
        self.assertTrue(self.error_handled)

    def test_custom_error_handler_with_unknown_error(self):
        with self.assertLogs(level="ERROR") as log:
            custom_error_handler(TypeError(), {ValueError: lambda e: None})
            self.assertIn("Unhandled error: ", log.output[0])

    def test_custom_error_handler_with_multiple_errors(self):
        def handle_value_error(e):
            self.value_error_handled = True

        def handle_type_error(e):
            self.type_error_handled = True

        self.value_error_handled = False
        self.type_error_handled = False

        custom_error_handler(
            ValueError(), {ValueError: handle_value_error, TypeError: handle_type_error}
        )
        self.assertTrue(self.value_error_handled)
        self.assertFalse(self.type_error_handled)

    def test_max_concurrent(self):
        async def async_func(x):
            await asyncio.sleep(0.1)
            return x

        limited_func = max_concurrent(async_func, 2)

        loop = asyncio.get_event_loop()
        tasks = [limited_func(i) for i in range(4)]
        results = loop.run_until_complete(asyncio.gather(*tasks))
        self.assertEqual(results, [0, 1, 2, 3])

    def test_max_concurrent_limit(self):
        async def async_func(x):
            await asyncio.sleep(0.1)
            return x

        limited_func = max_concurrent(async_func, 1)

        loop = asyncio.get_event_loop()
        tasks = [limited_func(i) for i in range(2)]
        results = loop.run_until_complete(asyncio.gather(*tasks))
        self.assertEqual(results, [0, 1])

    def test_max_concurrent_with_sync_func(self):
        def sync_func(x):
            time.sleep(0.1)
            return x

        limited_func = max_concurrent(sync_func, 2)

        loop = asyncio.get_event_loop()
        tasks = [limited_func(i) for i in range(4)]
        results = loop.run_until_complete(asyncio.gather(*tasks))
        self.assertEqual(results, [0, 1, 2, 3])

    def test_throttle_async_func(self):
        async def async_func(x):
            return x

        throttled_func = throttle(async_func, 1)

        loop = asyncio.get_event_loop()
        result1 = loop.run_until_complete(throttled_func(1))
        result2 = loop.run_until_complete(throttled_func(2))
        self.assertEqual(result1, 1)
        self.assertEqual(result2, 2)

    def test_throttle_with_short_period(self):
        async def async_func(x):
            return x

        throttled_func = throttle(async_func, 0.1)

        loop = asyncio.get_event_loop()
        result1 = loop.run_until_complete(throttled_func(1))
        result2 = loop.run_until_complete(throttled_func(2))
        self.assertEqual(result1, 1)
        self.assertEqual(result2, 2)

    def test_throttle_sync_func(self):
        def sync_func(x):
            return x

        throttled_func = throttle(sync_func, 1)

        loop = asyncio.get_event_loop()
        result1 = loop.run_until_complete(throttled_func(1))
        result2 = loop.run_until_complete(throttled_func(2))
        self.assertEqual(result1, 1)
        self.assertEqual(result2, 2)

    def test_force_async_with_args_and_kwargs(self):
        def sync_func(x, y=1):
            return x * y

        async_func = force_async(sync_func)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(async_func(2, y=3))
        self.assertEqual(result, 6)

    def test_force_async_with_return_none(self):
        def sync_func(x):
            return None

        async_func = force_async(sync_func)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(async_func(2))
        self.assertIsNone(result)

    def test_is_coroutine_func_with_partial(self):
        async def async_func(x, y):
            return x + y

        partial_func = functools.partial(async_func, 1)
        self.assertTrue(is_coroutine_func(partial_func))

    def test_is_coroutine_func_with_decorated_async(self):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            return wrapper

        @decorator
        async def async_func():
            pass

        self.assertTrue(is_coroutine_func(async_func))

    def test_custom_error_handler_with_error_subclass(self):
        class CustomError(ValueError):
            pass

        def handle_value_error(e):
            self.error_handled = True

        self.error_handled = False
        custom_error_handler(CustomError(), {ValueError: handle_value_error})
        self.assertTrue(self.error_handled)

    def test_custom_error_handler_with_multiple_handlers(self):
        def handle_value_error_1(e):
            self.value_error_handled_1 = True

        def handle_value_error_2(e):
            self.value_error_handled_2 = True

        def handle_value_error(e):
            handle_value_error_1(e)
            handle_value_error_2(e)

        self.value_error_handled_1 = False
        self.value_error_handled_2 = False

        custom_error_handler(ValueError(), {ValueError: handle_value_error})
        self.assertTrue(self.value_error_handled_1)
        self.assertTrue(self.value_error_handled_2)

    def test_max_concurrent_with_exception(self):
        async def async_func(x):
            if x == 1:
                raise ValueError("Test exception")
            await asyncio.sleep(0.1)
            return x

        limited_func = max_concurrent(async_func, 2)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [limited_func(i) for i in range(4)]
        with self.assertRaises(ValueError):
            loop.run_until_complete(asyncio.gather(*tasks))

    def test_max_concurrent_with_different_limits(self):
        async def async_func(x):
            await asyncio.sleep(0.3)
            return x

        limited_func_1 = max_concurrent(async_func, 1)
        limited_func_2 = max_concurrent(async_func, 2)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks_1 = [limited_func_1(i) for i in range(2)]
        tasks_2 = [limited_func_2(i) for i in range(4)]

        start_time_1 = loop.time()
        results_1 = loop.run_until_complete(asyncio.gather(*tasks_1))
        end_time_1 = loop.time()

        start_time_2 = loop.time()
        results_2 = loop.run_until_complete(asyncio.gather(*tasks_2))
        end_time_2 = loop.time()

        self.assertEqual(results_1, [0, 1])
        self.assertGreater(end_time_1 - start_time_1, 0.6)

        self.assertEqual(results_2, [0, 1, 2, 3])
        self.assertGreater(end_time_2 - start_time_2, 0.6)
        self.assertLess(end_time_2 - start_time_2, 0.9)

    def test_throttle_with_multiple_calls(self):
        async def async_func(x):
            return x

        throttled_func = throttle(async_func, 0.1)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_time = loop.time()
        results = loop.run_until_complete(
            asyncio.gather(throttled_func(1), throttled_func(2), throttled_func(3))
        )
        end_time = loop.time()

        self.assertEqual(results, [1, 2, 3])
        self.assertGreater(end_time - start_time, 0.2)

    def test_throttle_with_exception(self):
        async def async_func(x):
            if x == 1:
                raise ValueError("Test exception")
            return x

        throttled_func = throttle(async_func, 0.1)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        with self.assertRaises(ValueError):
            loop.run_until_complete(throttled_func(1))


class TestCallDecorator(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    async def async_func(self, x):
        await asyncio.sleep(0.1)
        return x * 2

    async def error_func(self, x):
        await asyncio.sleep(0.1)
        raise ValueError("Test exception")

    def sync_func(self, x):
        sleep(0.1)
        return x * 2

    def sync_error_func(self, x):
        sleep(0.1)
        raise ValueError("Test exception")

    # Tests for retry decorator
    def test_retry_async_success(self):
        func = CallDecorator.retry(retries=3)(self.async_func)
        result = self.loop.run_until_complete(func(3))
        self.assertEqual(result, 6)

    def test_retry_async_failure_with_default(self):
        func = CallDecorator.retry(retries=3, default="Default")(self.error_func)
        result = self.loop.run_until_complete(func(3))
        self.assertEqual(result, "Default")

    def test_retry_sync_success(self):
        func = CallDecorator.retry(retries=3)(self.sync_func)
        result = self.loop.run_until_complete(func(3))
        self.assertEqual(result, 6)

    def test_retry_sync_failure_with_default(self):
        func = CallDecorator.retry(retries=3, default="Default")(self.sync_error_func)
        result = self.loop.run_until_complete(func(3))
        self.assertEqual(result, "Default")

    def test_retry_with_backoff(self):
        func = CallDecorator.retry(retries=3, delay=0.1, backoff_factor=2)(
            self.error_func
        )
        with self.assertRaises(RuntimeError):
            self.loop.run_until_complete(func(3))

    # Tests for throttle decorator
    def test_throttle_async(self):
        func = CallDecorator.throttle(period=1)(self.async_func)
        start_time = self.loop.time()
        result1 = self.loop.run_until_complete(func(2))
        result2 = self.loop.run_until_complete(func(2))
        end_time = self.loop.time()
        self.assertEqual(result1, 4)
        self.assertEqual(result2, 4)
        self.assertGreaterEqual(end_time - start_time, 1)

    def test_throttle_sync(self):
        func = CallDecorator.throttle(period=1)(self.sync_func)
        start_time = self.loop.time()
        result1 = self.loop.run_until_complete(func(2))
        result2 = self.loop.run_until_complete(func(2))
        end_time = self.loop.time()
        self.assertEqual(result1, 4)
        self.assertEqual(result2, 4)
        self.assertGreaterEqual(end_time - start_time, 1)

    # Tests for max_concurrent decorator
    async def long_running_func(self, x):
        await asyncio.sleep(0.5)
        return x * 2

    def test_max_concurrent(self):
        func = CallDecorator.max_concurrent(limit=2)(self.long_running_func)
        start_time = self.loop.time()
        tasks = [func(i) for i in range(4)]
        self.loop.run_until_complete(asyncio.gather(*tasks))
        end_time = self.loop.time()
        self.assertGreaterEqual(end_time - start_time, 1.0)

    # Tests for compose decorator
    def test_compose_sync_functions(self):
        def inc(x):
            return x + 1

        def double(x):
            return x * 2

        func = CallDecorator.compose(inc, double)(self.sync_func)
        result = self.loop.run_until_complete(func(2))
        self.assertEqual(result, 10)

    def test_compose_async_functions(self):
        async def inc(x):
            return x + 1

        async def double(x):
            return x * 2

        func = CallDecorator.compose(inc, double)(self.async_func)
        result = self.loop.run_until_complete(func(2))
        self.assertEqual(result, 10)

    def test_compose_mixed_functions(self):
        async def inc(x):
            return x + 1

        def double(x):
            return x * 2

        CallDecorator.compose(inc, double)

    # Tests for pre_post_process decorator
    async def preprocess(self, x):
        return x + 1

    async def postprocess(self, x):
        return x * 2

    def test_pre_post_process_async(self):
        func = CallDecorator.pre_post_process(
            preprocess=self.preprocess, postprocess=self.postprocess
        )(self.async_func)
        result = self.loop.run_until_complete(func(2))
        self.assertEqual(result, 12)

    def test_pre_post_process_sync(self):
        def sync_preprocess(x):
            return x + 1

        def sync_postprocess(x):
            return x * 2

        func = CallDecorator.pre_post_process(
            preprocess=sync_preprocess, postprocess=sync_postprocess
        )(self.sync_func)
        result = self.loop.run_until_complete(func(2))
        self.assertEqual(result, 12)

    # Tests for cache decorator
    def test_cache_async(self):
        func = CallDecorator.cache(ttl=1)(self.async_func)
        result1 = self.loop.run_until_complete(func(2))
        result2 = self.loop.run_until_complete(func(2))
        self.assertEqual(result1, result2)

    def test_cache_expiry(self):
        func = CallDecorator.cache(ttl=1)(self.async_func)
        result1 = self.loop.run_until_complete(func(2))
        sleep(1.1)
        result2 = self.loop.run_until_complete(func(2))
        self.assertEqual(result1, result2)

    def test_retry_error_map(self):
        def error_handler(exc):
            raise RuntimeError("Custom error")

        error_map = {ValueError: error_handler}
        func = CallDecorator.retry(retries=3, error_map=error_map)(self.error_func)
        with self.assertRaises(RuntimeError):
            self.loop.run_until_complete(func(3))

    def test_retry_timeout(self):
        async def timeout_func(x):
            await asyncio.sleep(1)
            return x * 2

        func = CallDecorator.retry(retries=3, timeout=0.5)(timeout_func)
        with self.assertRaises(RuntimeError):
            self.loop.run_until_complete(func(3))

    def test_throttle_burst(self):
        func = CallDecorator.throttle(period=1)(self.async_func)
        start_time = self.loop.time()
        tasks = [func(i) for i in range(3)]
        results = self.loop.run_until_complete(asyncio.gather(*tasks))
        end_time = self.loop.time()
        self.assertLess(end_time - start_time, 3)
        self.assertEqual(results, [0, 2, 4])

    def test_max_concurrent_sync(self):
        func = CallDecorator.max_concurrent(limit=2)(self.sync_func)
        start_time = self.loop.time()
        tasks = [func(i) for i in range(4)]
        results = self.loop.run_until_complete(
            asyncio.gather(*[asyncio.Task(t) for t in tasks])
        )
        end_time = self.loop.time()
        self.assertGreaterEqual(end_time - start_time, 0.2)
        self.assertEqual(results, [0, 2, 4, 6])

    def test_compose_exception(self):
        def inc(x):
            return x + 1

        def error(x):
            raise ValueError("Test exception")

        func = CallDecorator.compose(inc, error)(self.sync_func)
        with self.assertRaises(ValueError):
            self.loop.run_until_complete(func(2))

    def test_pre_post_process_kwargs(self):
        async def preprocess(x, y):
            return x + y

        async def postprocess(x, z):
            return x * z

        func = CallDecorator.pre_post_process(
            preprocess=preprocess,
            postprocess=postprocess,
            preprocess_kwargs={"y": 2},
            postprocess_kwargs={"z": 3},
        )(self.async_func)
        result = self.loop.run_until_complete(func(2))
        self.assertEqual(result, 24)

    def test_cache_sync(self):
        func = CallDecorator.cache(maxsize=2)(self.sync_func)
        result1 = func(2)
        result2 = func(2)
        self.assertEqual(result1, result2)

    def test_cache_clear(self):
        func = CallDecorator.cache(ttl=1)(self.async_func)
        result1 = self.loop.run_until_complete(func(2))
        result2 = self.loop.run_until_complete(func(2))
        self.assertEqual(result1, result2)


if __name__ == "__main__":
    unittest.main()

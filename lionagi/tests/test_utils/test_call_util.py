# import unittest
# import asyncio
# import time
# import lionagi.utils.call_util as call_util
# from lionagi.utils.call_util import CallDecorator
# from lionagi.utils.call_util import Throttle


# class TestToList(unittest.TestCase):

#     def test_empty_input(self):
#         self.assertEqual(call_util.to_list([]), [])

#     def test_single_element(self):
#         self.assertEqual(call_util.to_list(5), [5])

#     def test_list_input(self):
#         self.assertEqual(call_util.to_list([1, [2, 3]], flatten=False), [1, [2, 3]])

#     def test_nested_list(self):
#         self.assertEqual(call_util.to_list([[1, 2], [3, 4]], flatten=True), [1, 2, 3, 4])

#     def test_non_list_iterable(self):
#         self.assertEqual(call_util.to_list((1, 2, 3)), [1, 2, 3])

#     def test_string_handling(self):
#         self.assertEqual(call_util.to_list("abc"), ["abc"])

#     def test_drop_none(self):
#         self.assertEqual(call_util.to_list([1, None, 2], dropna=True), [1, 2])

#     class FaultyIterable:
#         """An iterable class that raises an exception when iterated over."""

#         def __iter__(self):
#             return self

#         def __next__(self):
#             raise RuntimeError("Fault during iteration")

#     def test_invalid_input(self):
#         with self.assertRaises(ValueError):
#             call_util.to_list(TestToList.FaultyIterable())


# class TestLCall(unittest.TestCase):

#     def test_empty_input(self):
#         self.assertEqual(call_util.lcall([], lambda x: x*2), [])

#     def test_single_element(self):
#         self.assertEqual(call_util.lcall(5, lambda x: x*2), [10])

#     def test_list_input_with_simple_function(self):
#         self.assertEqual(call_util.lcall([1, 2, 3], lambda x: x*2), [2, 4, 6])

#     def test_flatten(self):
#         self.assertEqual(call_util.lcall([[1, 2], [3, 4]], lambda x: x*2, flatten=True), [2, 4, 6, 8])

#     def test_drop_none(self):
#         self.assertEqual(call_util.lcall([1, None, 2], lambda x: x, dropna=True), [1, 2])

#     def test_with_lambda_function(self):
#         self.assertEqual(call_util.lcall([1, 2, 3], lambda x: x + 1), [2, 3, 4])

#     def test_exception_handling(self):
#         def faulty_func(x):
#             raise ValueError("Faulty Function")
#         with self.assertRaises(ValueError):
#             call_util.lcall([1, 2, 3], faulty_func)

#     def test_with_additional_arguments(self):
#         self.assertEqual(call_util.lcall([1, 2, 3], lambda x, y: x + y, y=2), [3, 4, 5])


# class TestAlCall(unittest.IsolatedAsyncioTestCase):

#     async def test_empty_input(self):
#         result = await call_util.alcall([], lambda x: x*2)
#         self.assertEqual(result, [])

#     async def test_single_element_with_async_function(self):
#         async def async_func(x):
#             return x * 2
#         result = await call_util.alcall(5, async_func)
#         self.assertEqual(result, [10])

#     async def test_list_input_with_sync_function(self):
#         result = await call_util.alcall([1, 2, 3], lambda x: x*2)
#         self.assertEqual(result, [2, 4, 6])

#     async def test_flatten_with_async_function(self):
#         async def async_func(x):
#             return x * 2
#         result = await call_util.alcall([[1, 2], [3, 4]], async_func, flatten=True)
#         self.assertEqual(result, [2, 4, 6, 8])

#     async def test_drop_none_with_sync_function(self):
#         result = await call_util.alcall([1, None, 2], lambda x: x, dropna=True)
#         self.assertEqual(result, [1, 2])

#     async def test_exception_handling_in_async_function(self):
#         async def faulty_func(x):
#             raise ValueError("Faulty Function")
#         with self.assertRaises(ValueError):
#             await call_util.alcall([1, 2, 3], faulty_func)

#     async def test_with_additional_arguments(self):
#         async def async_func(x, y):
#             return x + y
#         result = await call_util.alcall([1, 2, 3], async_func, y=2)
#         self.assertEqual(result, [3, 4, 5])


# class TestTCall(unittest.IsolatedAsyncioTestCase):

#     async def test_sync_function_call(self):
#         def sync_func(x):
#             return x * 2
#         result = await call_util.tcall(5, sync_func)
#         self.assertEqual(result, 10)

#     async def test_async_function_call(self):
#         async def async_func(x):
#             return x * 2
#         result = await call_util.tcall(5, async_func)
#         self.assertEqual(result, 10)

#     async def test_with_delay(self):
#         async def async_func(x):
#             return x * 2
#         start_time = asyncio.get_event_loop().time()
#         await call_util.tcall(5, async_func, sleep=1)
#         elapsed = asyncio.get_event_loop().time() - start_time
#         self.assertTrue(elapsed >= 1)

#     async def test_error_handling(self):
#         async def async_func(x):
#             raise ValueError("Test Error")
#         with self.assertRaises(ValueError):
#             await call_util.tcall(5, async_func, message="Custom Error Message")

#     async def test_execution_timing(self):
#         async def async_func(x):
#             return x * 2
#         result, duration = await call_util.tcall(5, async_func, include_timing=True)
#         self.assertEqual(result, 10)
#         self.assertIsInstance(duration, float)

#     async def test_ignore_error(self):
#         def sync_func(x):
#             raise ValueError("Test Error")
#         result = await call_util.tcall(5, sync_func, ignore_error=True)
#         self.assertIsNone(result)

#     async def test_with_additional_arguments(self):
#         async def async_func(x, y):
#             return x + y
#         result = await call_util.tcall(5, async_func, y=3)
#         self.assertEqual(result, 8)

# class TestMCall(unittest.IsolatedAsyncioTestCase):

#     async def test_single_function_single_input(self):
#         async def async_func(x):
#             return x * 2
#         result = await call_util.mcall(5, async_func)
#         self.assertEqual(result, [10])

#     async def test_list_of_functions_single_input(self):
#         async def async_func1(x):
#             return x * 2
#         async def async_func2(x):
#             return x + 3
#         with self.assertRaises(AssertionError):
#             await call_util.mcall(5, [async_func1, async_func2])

#     async def test_single_function_list_of_inputs(self):
#         async def async_func(x):
#             return x * 2

#         with self.assertRaises(AssertionError):
#             await call_util.mcall([1, 2, 3], async_func)

#     async def test_list_of_functions_list_of_inputs_explode_false(self):
#         async def async_func1(x):
#             return x * 2
#         async def async_func2(x):
#             return x + 3
#         result = await call_util.mcall([1, 2], [async_func1, async_func2])
#         self.assertEqual(result, [2, 5])

#     async def test_list_of_functions_list_of_inputs_explode_true(self):
#         async def async_func1(x):
#             return x * 2
#         async def async_func2(x):
#             return x + 3
#         result = await call_util.mcall([1, 2], [async_func1, async_func2], explode=True)
#         self.assertEqual(result, [[2, 4], [4, 5]])

#     async def test_flatten_and_dropna(self):
#         async def async_func1(x):
#             return x * 2
#         async def async_func2(x):
#             return x + 3
#         result = await call_util.mcall([[1, None], [None, 2]], [async_func1, async_func2], flatten=True, dropna=True)
#         self.assertEqual(result, [2, 5])

#     async def test_exception_handling(self):
#         async def async_func(x):
#             if x == 2:
#                 raise ValueError("Test Error")
#             return x * 2
#         with self.assertRaises(ValueError):
#             await call_util.mcall([1, 2], [async_func, async_func])

#     async def test_with_additional_arguments(self):
#         async def async_func(x, y):
#             return x + y
#         result = await call_util.mcall([1, 2], [async_func, async_func], y=2)
#         self.assertEqual(result, [3, 4])

# class TestBCall(unittest.IsolatedAsyncioTestCase):

#     async def test_empty_input_list(self):
#         async def async_func(x):
#             return x * 2
#         result = await call_util.bcall([], async_func, batch_size=2)
#         self.assertEqual(result, [])

#     async def test_sync_function_call(self):
#         def sync_func(x):
#             return x * 2
#         result = await call_util.bcall([1, 2, 3], sync_func, batch_size=2)
#         self.assertEqual(result, [2, 4, 6])

#     async def test_async_function_call(self):
#         async def async_func(x):
#             return x * 2
#         result = await call_util.bcall([1, 2, 3], async_func, batch_size=2)
#         self.assertEqual(result, [2, 4, 6])

#     async def test_batch_processing(self):
#         async def async_func(x):
#             return x * 2
#         # Test with 4 elements and a batch size of 2
#         result = await call_util.bcall([1, 2, 3, 4], async_func, batch_size=2)
#         self.assertEqual(result, [2, 4, 6, 8])

#     async def test_exception_handling(self):
#         async def async_func(x):
#             if x == 2:
#                 raise ValueError("Test Error")
#             return x * 2
#         with self.assertRaises(ValueError):
#             await call_util.bcall([1, 2, 3], async_func, batch_size=2)

#     async def test_with_additional_arguments(self):
#         async def async_func(x, y):
#             return x + y
#         result = await call_util.bcall([1, 2, 3], async_func, batch_size=2, y=3)
#         self.assertEqual(result, [4, 5, 6])


# class TestRCall(unittest.IsolatedAsyncioTestCase):

#     async def test_sync_function_without_timeout(self):
#         def sync_func(x):
#             return x * 2
#         result = await call_util.rcall(sync_func, 5)
#         self.assertEqual(result, 10)

#     async def test_async_function_without_timeout(self):
#         async def async_func(x):
#             return x * 2
#         result = await call_util.rcall(async_func, 5)
#         self.assertEqual(result, 10)

#     async def test_timeout(self):
#         async def async_func(x):
#             await asyncio.sleep(2)
#             return x
#         with self.assertRaises(asyncio.TimeoutError):
#             await call_util.rcall(async_func, 5, timeout=1)

#     async def test_timeout(self):
#         def async_func(x):
#             time.sleep(2)
#             return x
#         with self.assertRaises(asyncio.TimeoutError):
#             await call_util.rcall(async_func, 5, timeout=1)

#     async def test_retry_mechanism(self):
#         attempt_count = 0
#         def sync_func(x):
#             nonlocal attempt_count
#             attempt_count += 1
#             raise ValueError("Test Error")
#         with self.assertRaises(ValueError):
#             await call_util.rcall(sync_func, 5, retries=3)
#         self.assertEqual(attempt_count, 4)  # Initial call + 3 retries

#     async def test_default_value_on_exception(self):
#         def sync_func(x):
#             raise ValueError("Test Error")
#         result = await call_util.rcall(sync_func, 5, default=10)
#         self.assertEqual(result, 10)

#     async def test_exception_propagation(self):
#         def sync_func(x):
#             raise ValueError("Test Error")
#         with self.assertRaises(ValueError):
#             await call_util.rcall(sync_func, 5)


# class TestCallDecorator(unittest.IsolatedAsyncioTestCase):

#     def test_cache_decorator_sync(self):
#         @CallDecorator.cache
#         def sync_func(x):
#             return x * 2

#         first_call = sync_func(5)
#         second_call = sync_func(5)

#         self.assertEqual(first_call, 10)
#         self.assertIs(first_call, second_call)

#     async def test_cache_decorator_async(self):
#         @CallDecorator.cache
#         async def async_func(x):
#             return x * 2

#         first_call = await async_func(5)
#         second_call = await async_func(5)

#         self.assertEqual(first_call, 10)
#         self.assertIs(first_call, second_call)

#     def test_timeout_with_sync_function(self):
#         @CallDecorator.timeout(1)  # 1 second timeout
#         def sync_func(x):
#             time.sleep(2)  # Sleep for 2 seconds, should trigger timeout
#             return x

#         with self.assertRaises(asyncio.TimeoutError):
#             asyncio.run(sync_func(5))

#     def test_no_timeout_with_sync_function(self):
#         @CallDecorator.timeout(2)  # 2 second timeout
#         def sync_func(x):
#             time.sleep(1)  # Sleep for 1 second, within timeout
#             return x

#         result = sync_func(5)
#         self.assertEqual(result, 5)

#     async def test_timeout_with_async_function(self):
#         @CallDecorator.timeout(1)  # 1 second timeout
#         async def async_func(x):
#             await asyncio.sleep(2)  # Sleep for 2 seconds, should trigger timeout
#             return x

#         with self.assertRaises(asyncio.TimeoutError):
#             await async_func(5)

#     async def test_no_timeout_with_async_function(self):
#         @CallDecorator.timeout(2)  # 2 second timeout
#         async def async_func(x):
#             await asyncio.sleep(1)  # Sleep for 1 second, within timeout
#             return x

#         result = await async_func(5)
#         self.assertEqual(result, 5)

#     def test_successful_retry(self):
#         attempt = 0

#         @CallDecorator.retry(retries=3, initial_delay=1, backoff_factor=2)
#         def test_func():
#             nonlocal attempt
#             attempt += 1
#             if attempt < 3:
#                 raise ValueError("Test failure")
#             return "Success"

#         result = test_func()
#         self.assertEqual(result, "Success")
#         self.assertEqual(attempt, 3)

#     def test_retry_limit(self):
#         attempt = 0

#         @CallDecorator.retry(retries=2, initial_delay=1, backoff_factor=2)
#         def test_func():
#             nonlocal attempt
#             attempt += 1
#             raise ValueError("Test failure")

#         with self.assertRaises(ValueError):
#             test_func()
#         self.assertEqual(attempt, 3)

#     def test_immediate_success(self):
#         attempt = 0

#         @CallDecorator.retry(retries=3, initial_delay=1, backoff_factor=2)
#         def test_func():
#             nonlocal attempt
#             attempt += 1
#             return "Success"


#         result = test_func()
#         self.assertEqual(result, "Success")
#         self.assertEqual(attempt, 1)

#     def test_retry_with_delays(self):
#         attempt = 0
#         start_time = time.time()

#         @CallDecorator.retry(retries=3, initial_delay=1, backoff_factor=2)
#         def test_func():
#             nonlocal attempt
#             attempt += 1
#             if attempt < 3:
#                 raise ValueError("Test failure")
#             return "Success"

#         result = test_func()
#         end_time = time.time()
#         elapsed_time = end_time - start_time

#         self.assertEqual(result, "Success")
#         self.assertTrue(elapsed_time >= 3)
#         self.assertEqual(attempt, 3)

#     def test_default_value_on_exception(self):
#         @CallDecorator.default(default_value="Default")
#         def test_func():
#             raise ValueError("Test failure")

#         result = test_func()
#         self.assertEqual(result, "Default")

#     def test_no_exception(self):
#         @CallDecorator.default(default_value="Default")
#         def test_func():
#             return "Success"

#         result = test_func()
#         self.assertEqual(result, "Success")

#     def test_throttling_behavior(self):
#         @CallDecorator.throttle(period=2)  # 2 seconds throttle period
#         def test_func():
#             return time.time()

#         start_time = time.time()
#         first_call = test_func()
#         second_call = test_func()
#         end_time = time.time()

#         self.assertLess(first_call - start_time, 1)  # First call should be immediate
#         self.assertGreaterEqual(second_call - first_call, 2)  # Second call should be delayed
#         self.assertLessEqual(end_time - start_time, 3)  # Total time should be within reasonable bounds

#     def test_successive_calls_outside_throttle_period(self):
#         @CallDecorator.throttle(period=1)  # 1 second throttle period
#         def test_func():
#             return time.time()

#         first_call = test_func()
#         time.sleep(1.1)  # Sleep to exceed the throttle period
#         second_call = test_func()

#         self.assertGreaterEqual(second_call - first_call, 1)  # Second call should not be delayed

#     def test_throttling_with_different_inputs(self):
#         @CallDecorator.throttle(period=2)  # 2 seconds throttle period
#         def test_func(x):
#             return x

#         first_call = test_func(1)
#         time.sleep(0.5)
#         second_call = test_func(2)

#         self.assertEqual(first_call, 1)
#         self.assertEqual(second_call, 2)  # Should return the result of the first call due to throttling

#     def test_preprocessing(self):
#         def preprocess(x):
#             return x * 2

#         @CallDecorator.pre_post_process(preprocess, lambda x: x)
#         def test_func(x):
#             return x + 3

#         result = test_func(2)  # Preprocess: 2 * 2 -> 4, Func: 4 + 3
#         self.assertEqual(result, 7)

#     def test_postprocessing(self):
#         def postprocess(x):
#             return x * 3

#         @CallDecorator.pre_post_process(lambda x: x, postprocess)
#         def test_func(x):
#             return x + 2

#         result = test_func(2)  # Func: 2 + 2 -> 4, Postprocess: 4 * 3
#         self.assertEqual(result, 12)


#     def test_preprocessing_and_postprocessing(self):
#         def preprocess(x):
#             return x * 2

#         def postprocess(x):
#             return x * 3

#         @CallDecorator.pre_post_process(preprocess, postprocess)
#         def test_func(x):
#             return x + 1

#         result = test_func(2)  # Preprocess: 2 * 2 -> 4, Func: 4 + 1 -> 5, Postprocess: 5 * 3
#         self.assertEqual(result, 15)

#     def test_filtering_based_on_predicate(self):
#         is_even = lambda x: x % 2 == 0

#         @CallDecorator.filter(is_even)
#         def test_func():
#             return [1, 2, 3, 4, 5]

#         result = test_func()
#         self.assertEqual(result, [2, 4])

#     def test_no_items_satisfy_predicate(self):
#         is_negative = lambda x: x < 0

#         @CallDecorator.filter(is_negative)
#         def test_func():
#             return [1, 2, 3, 4, 5]

#         result = test_func()
#         self.assertEqual(result, [])

#     def test_all_items_satisfy_predicate(self):
#         is_positive = lambda x: x > 0

#         @CallDecorator.filter(is_positive)
#         def test_func():
#             return [1, 2, 3, 4, 5]

#         result = test_func()
#         self.assertEqual(result, [1, 2, 3, 4, 5])

#     def test_mapping_function(self):
#         double = lambda x: x * 2

#         @CallDecorator.map(double)
#         def test_func():
#             return [1, 2, 3, 4, 5]

#         result = test_func()
#         self.assertEqual(result, [2, 4, 6, 8, 10])

#     def test_empty_list(self):
#         double = lambda x: x * 2

#         @CallDecorator.map(double)
#         def test_func():
#             return []

#         result = test_func()
#         self.assertEqual(result, [])

#     def test_mapping_with_different_data_types(self):
#         to_string = lambda x: str(x)

#         @CallDecorator.map(to_string)
#         def test_func():
#             return [1, 2.5, 'test', True]

#         result = test_func()
#         self.assertEqual(result, ['1', '2.5', 'test', 'True'])

#     def test_reduction_function(self):
#         sum_func = lambda x, y: x + y

#         @CallDecorator.reduce(sum_func, 0)
#         def test_func():
#             return [1, 2, 3, 4, 5]

#         result = test_func()
#         self.assertEqual(result, 15)  # Sum of 1, 2, 3, 4, 5

#     def test_empty_list(self):
#         sum_func = lambda x, y: x + y

#         @CallDecorator.reduce(sum_func, 0)
#         def test_func():
#             return []

#         result = test_func()
#         self.assertEqual(result, 0)  # Initial value

#     def test_reduction_with_initial_value(self):
#         sum_func = lambda x, y: x + y

#         @CallDecorator.reduce(sum_func, 10)
#         def test_func():
#             return [1, 2, 3, 4, 5]

#         result = test_func()
#         self.assertEqual(result, 25)  # 10 (initial) + Sum of 1, 2, 3, 4, 5

#     def test_function_composition(self):
#         double = lambda x: x * 2
#         add_five = lambda x: x + 5

#         @CallDecorator.compose(add_five, double)  # First add_five, then double
#         def test_func():
#             return 3

#         result = test_func()
#         self.assertEqual(result, (3 + 5) * 2)

#     def test_empty_function_list(self):
#         @CallDecorator.compose()
#         def test_func():
#             return "test"

#         result = test_func()
#         self.assertEqual(result, "test")

#     def test_error_handling_in_composition(self):
#         def raise_error(x):
#             raise ValueError("Error in function")

#         @CallDecorator.compose(raise_error)
#         def test_func():
#             return 3

#         with self.assertRaises(ValueError):
#             test_func()

#     def test_caching_behavior(self):
#         @CallDecorator.memorize(maxsize=10)
#         def test_func(x):
#             return x * 2

#         first_call = test_func(5)
#         second_call = test_func(5)

#         self.assertEqual(first_call, 10)
#         self.assertIs(first_call, second_call)  # Should return cached result

#     def test_different_arguments(self):
#         @CallDecorator.memorize(maxsize=10)
#         def test_func(x):
#             return x * 2

#         first_call = test_func(5)
#         second_call = test_func(6)

#         self.assertNotEqual(first_call, second_call)
#         self.assertIsNot(first_call, second_call)

#     def test_cache_size_limit(self):
#         @CallDecorator.memorize(maxsize=2)
#         def test_func(x):
#             return x * 2

#         test_func(1)  # Cache this
#         test_func(2)  # Cache this
#         test_func(3)  # Cache should evict the first entry (1)
#         result = test_func(1)  # Recompute as it should be evicted

#         self.assertEqual(result, 2)

#     def test_type_validation(self):
#         @CallDecorator.validate(validate_type=int)
#         def test_func():
#             return 5

#         result = test_func()
#         self.assertEqual(result, 5)

#     def test_type_conversion(self):
#         @CallDecorator.validate(convert_type=str)
#         def test_func():
#             return 5

#         result = test_func()
#         self.assertEqual(result, "5")

#     def test_error_handling_on_invalid_type(self):
#         @CallDecorator.validate(validate_type=int)
#         def test_func():
#             return "not an int"

#         with self.assertRaises(TypeError):
#             test_func()

#     def test_default_value_on_error(self):
#         @CallDecorator.validate(validate_type=int, handle_error={'default': 0})
#         def test_func():
#             return "not an int"

#         result = test_func()
#         self.assertEqual(result, 0)

#     async def test_concurrency_limit(self):
#         current_concurrency = 0
#         max_concurrent_calls = 0

#         @CallDecorator.max_concurrency(limit=2)
#         async def test_func():
#             nonlocal current_concurrency, max_concurrent_calls
#             current_concurrency += 1
#             max_concurrent_calls = max(max_concurrent_calls, current_concurrency)
#             await asyncio.sleep(0.1)  # Simulate async work
#             current_concurrency -= 1

#         await asyncio.gather(*(test_func() for _ in range(5)))
#         self.assertEqual(max_concurrent_calls, 2)

#     async def test_function_completing_within_limit(self):
#         @CallDecorator.max_concurrency(limit=2)
#         async def test_func(x):
#             await asyncio.sleep(0.1)
#             return x

#         results = await asyncio.gather(*(test_func(i) for i in range(5)))
#         self.assertEqual(results, [0, 1, 2, 3, 4])


# class TestThrottleClass(unittest.TestCase):

#     def test_throttling_behavior_sync(self):
#         throttle_decorator = Throttle(2)  # 2 seconds throttle period

#         @throttle_decorator
#         def test_func():
#             return time.time()

#         first_call_time = test_func()
#         time.sleep(1)  # Sleep less than the throttle period
#         second_call_time = test_func()

#         self.assertGreaterEqual(second_call_time - first_call_time, 2)  # Second call should be throttled

#     def test_throttling_behavior_async(self):
#         throttle_decorator = Throttle(2)  # 2 seconds throttle period

#         @throttle_decorator
#         async def test_func():
#             return time.time()

#         async def async_test():
#             first_call_time = await test_func()
#             await asyncio.sleep(1)  # Sleep less than the throttle period
#             second_call_time = await test_func()

#             self.assertGreaterEqual(second_call_time - first_call_time, 2)  # Second call should be throttled

#         asyncio.run(async_test())

#     def test_successive_calls_with_sufficient_delay(self):
#         throttle_decorator = Throttle(1)  # 1 second throttle period

#         @throttle_decorator
#         def test_func():
#             return time.time()

#         first_call_time = test_func()
#         time.sleep(1.1)  # Sleep more than the throttle period
#         second_call_time = test_func()

#         self.assertLess(second_call_time - first_call_time, 1.5)  # Second call should not be throttled


# if __name__ == '__main__':
#     unittest.main()
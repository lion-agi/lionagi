# import asyncio
# import unittest
# from unittest.mock import patch, MagicMock
# from lionagi.utils.sys_util import create_copy
# from lionagi.utils.flat_util import to_list
# from typing import Callable

# # Assuming the Python module with the above functions is named 'call_utils'
# from lionagi.utils.call_util import *

# class TestCallUtils(unittest.TestCase):

#     def setUp(self):
#         self.sample_input = [1, 2, 3]
#         self.sample_func = MagicMock(return_value=42)
        
#     def test_hcall(self):
#         with patch('time.sleep', return_value=None):
#             result = hcall(self.sample_input, self.sample_func)
#             self.sample_func.assert_called_once_with(self.sample_input)
#             self.assertEqual(result, 42)

#     def test_ahcall(self):
#         async def async_test():
#             self.sample_func.reset_mock()
#             with patch('asyncio.sleep', return_value=None):
#                 result = await ahcall(self.sample_input, self.sample_func)
#                 self.sample_func.assert_called_once_with(self.sample_input)
#                 self.assertEqual(result, 42)

#         asyncio.run(async_test())

#     def test_lcall(self):
#         expected_result = [42, 42, 42]
#         result = lcall(self.sample_input, self.sample_func)
#         self.assertEqual(result, expected_result)
#         calls = [unittest.mock.call(item) for item in self.sample_input]
#         self.sample_func.assert_has_calls(calls, any_order=True)

#     def test_alcall(self):
#         async def async_test():
#             expected_result = [42, 42, 42]
#             self.sample_func.reset_mock()
#             result = await alcall(self.sample_input, self.sample_func)
#             self.assertEqual(result, expected_result)
#             calls = [unittest.mock.call(item) for item in self.sample_input]
#             self.sample_func.assert_has_calls(calls, any_order=True)

#         asyncio.run(async_test())


# class TestCallUtils2(unittest.TestCase):

#     def setUp(self):
#         self.sample_input = [1, 2, 3]
#         self.sample_func = MagicMock(side_effect=lambda x: x + 1)
#         self.sample_async_func = MagicMock(side_effect=lambda x: x + 1)
        
#     def test_mcall_single_function(self):
#         result = mcall(self.sample_input, self.sample_func)
#         self.sample_func.assert_has_calls([unittest.mock.call(i) for i in self.sample_input], any_order=True)
#         self.assertEqual(result, [2, 3, 4])

#     def test_mcall_multiple_functions(self):
#         # Define multiple functions
#         funcs = [
#             MagicMock(side_effect=lambda x: x + 1),
#             MagicMock(side_effect=lambda x: x * 2),
#             MagicMock(side_effect=lambda x: x - 1)
#         ]
#         result = mcall(self.sample_input, funcs)
#         for i, func in enumerate(funcs):
#             func.assert_called_once_with(self.sample_input[i])
#         self.assertEqual(result, [2, 4, 2])

#     def test_amcall_single_function(self):
#         async def async_test():
#             result = await amcall(self.sample_input, self.sample_async_func)
#             self.sample_async_func.assert_has_calls([unittest.mock.call(i) for i in self.sample_input], any_order=True)
#             self.assertEqual(result, [2, 3, 4])

#         asyncio.run(async_test())

#     def test_amcall_multiple_functions(self):
#         # Define multiple asynchronous functions
#         async_funcs = [
#             MagicMock(side_effect=lambda x: x + 1),
#             MagicMock(side_effect=lambda x: x * 2),
#             MagicMock(side_effect=lambda x: x - 1)
#         ]

#         async def async_test():
#             result = await amcall(self.sample_input, async_funcs)
#             for i, func in enumerate(async_funcs):
#                 func.assert_called_once_with(self.sample_input[i])
#             self.assertEqual(result, [2, 4, 2])

#         asyncio.run(async_test())

#     def test_ecall(self):
#         funcs = [MagicMock(side_effect=lambda x: x * x)]
#         result = ecall(self.sample_input, funcs)
#         self.assertEqual(result, [[1, 4, 9]])

#     def test_aecall(self):
#         async_funcs = [MagicMock(side_effect=lambda x: x * x)]

#         async def async_test():
#             result = await aecall(self.sample_input, async_funcs)
#             self.assertEqual(result, [[1, 4, 9]])

#         asyncio.run(async_test())

# if __name__ == '__main__':
#     unittest.main()
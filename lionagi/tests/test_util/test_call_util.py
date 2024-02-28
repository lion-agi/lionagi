import unittest
from lionagi.util.call_util import *

class TestToList(unittest.TestCase):
    def test_simple_list(self):
        self.assertEqual(to_list([1, 2, 3]), [1, 2, 3])

    def test_flatten_nested_list(self):
        self.assertEqual(to_list([1, [2, 3], 4], flatten=True), [1, 2, 3, 4])

    def test_dropna(self):
        self.assertEqual(to_list([1, None, 3], dropna=True), [1, 3])

    def test_non_list_input(self):
        self.assertEqual(to_list("hello", flatten=False), ["hello"])
        
class TestLCall(unittest.TestCase):
    def test_simple_function(self):
        result = lcall([1, 2, 3], lambda x: x * 2)
        self.assertEqual(result, [2, 4, 6])

    def test_function_returns_lists_flatten(self):
        result = lcall([1, 2], lambda x: [x, x], flatten=True)
        self.assertEqual(result, [1, 1, 2, 2])

    def test_function_returns_none_dropna(self):
        result = lcall([1, 2, None], lambda x: x if x else None, dropna=True)
        self.assertEqual(result, [1, 2])

    def test_function_with_kwargs(self):
        result = lcall([1, 2], lambda x, y: x + y, y=10)
        self.assertEqual(result, [11, 12])


if __name__ == '__main__':
    unittest.main()
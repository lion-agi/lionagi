import unittest
from unittest.mock import MagicMock

# Assuming the Python module with the above functions is named 'api_utils'
from lionagi.utils.api_util import *

class TestApiUtils(unittest.TestCase):

    def test_api_method_valid(self):
        session = MagicMock()
        methods = ['post', 'delete', 'head', 'options', 'patch']
        for method in methods:
            with self.subTest(method=method):
                func = api_method(session, method)
                self.assertTrue(callable(func))

    def test_api_method_invalid(self):
        session = MagicMock()
        with self.assertRaises(ValueError):
            api_method(session, 'get')

    def test_api_error(self):
        response_with_error = {'error': 'Something went wrong'}
        response_without_error = {'result': 'Success'}

        self.assertTrue(api_error(response_with_error))
        self.assertFalse(api_error(response_without_error))

    def test_api_rate_limit_error(self):
        response_with_rate_limit_error = {'error': {'message': 'Rate limit exceeded'}}
        response_without_rate_limit_error = {'error': {'message': 'Another error'}}

        self.assertTrue(api_rate_limit_error(response_with_rate_limit_error))
        self.assertFalse(api_rate_limit_error(response_without_rate_limit_error))

    def test_api_endpoint_from_url(self):
        url_with_endpoint = "https://api.example.com/v1/users"
        url_without_endpoint = "https://api.example.com/users"
        url_invalid = "Just a string"

        self.assertEqual(api_endpoint_from_url(url_with_endpoint), 'users')
        self.assertEqual(api_endpoint_from_url(url_without_endpoint), '')
        self.assertEqual(api_endpoint_from_url(url_invalid), '')

if __name__ == '__main__':
    unittest.main()
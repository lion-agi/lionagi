import aiohttp
import unittest
from unittest.mock import AsyncMock

from lionagi.libs.ln_api import *


class TestAPIUtil(unittest.TestCase):
    def test_api_method_post(self):
        session = AsyncMock(spec=aiohttp.ClientSession)
        method = APIUtil.api_method(session, "post")
        self.assertTrue(callable(method))

    def test_api_method_invalid(self):
        session = AsyncMock(spec=aiohttp.ClientSession)
        with self.assertRaises(ValueError):
            APIUtil.api_method(session, "invalid_method")


class TestAPIUtilExtended(unittest.TestCase):
    def test_api_error_with_error(self):
        response_json = {"error": "Something went wrong"}
        self.assertTrue(APIUtil.api_error(response_json))

    def test_api_error_without_error(self):
        response_json = {"result": "Success"}
        self.assertFalse(APIUtil.api_error(response_json))

    def test_api_rate_limit_error_with_rate_limit(self):
        response_json = {"error": {"message": "Rate limit exceeded"}}
        self.assertTrue(APIUtil.api_rate_limit_error(response_json))

    def test_api_rate_limit_error_without_rate_limit(self):
        response_json = {"error": {"message": "Another error"}}
        self.assertFalse(APIUtil.api_rate_limit_error(response_json))

    def test_api_endpoint_from_url_valid(self):
        valid_url = "https://api.example.com/v1/users"
        self.assertEqual(APIUtil.api_endpoint_from_url(valid_url), "users")

    def test_api_endpoint_from_url_invalid(self):
        invalid_url = "https://api.example.com/users"
        self.assertEqual(APIUtil.api_endpoint_from_url(invalid_url), "")


if __name__ == "__main__":
    unittest.main()

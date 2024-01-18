# import unittest
# import os
# import aiohttp
# import json
# import hashlib
# from aioresponses import aioresponses
# from lionagi.utils.api_util import APIUtil


# class TestAPIUtil(unittest.IsolatedAsyncioTestCase):

#     async def asyncSetUp(self):
#         self.session = aiohttp.ClientSession()
#         self.file_path = "test_file.txt"

#         with open(self.file_path, 'w') as f:
#             f.write("Test data")

#     async def asyncTearDown(self):
#         await self.session.close()
#         os.remove(self.file_path)

#     def test_api_method(self):
#         for method in ["post", "delete", "head", "options", "patch"]:
#             with self.subTest(method=method):
#                 http_method = APIUtil.api_method(self.session, method)
#                 self.assertTrue(callable(http_method))
#         with self.assertRaises(ValueError):
#             APIUtil.api_method(self.session, "invalid_method")

#     def test_api_error(self):
#         response_json_with_error = {"error": "Something went wrong"}
#         self.assertTrue(APIUtil.api_error(response_json_with_error))

#         response_json_without_error = {"result": "Success"}
#         self.assertFalse(APIUtil.api_error(response_json_without_error))

#     def test_api_rate_limit_error(self):
#         response_json_with_rate_limit = {"error": {"message": "Rate limit exceeded"}}
#         self.assertTrue(APIUtil.api_rate_limit_error(response_json_with_rate_limit))

#         response_json_without_rate_limit = {"error": {"message": "Another error"}}
#         self.assertFalse(APIUtil.api_rate_limit_error(response_json_without_rate_limit))

#     def test_api_endpoint_from_url(self):
#         # Test with valid URL
#         valid_url = "https://api.example.com/v1/users"
#         self.assertEqual(APIUtil.api_endpoint_from_url(valid_url), 'users')

#         # Test with another valid URL
#         another_valid_url = "https://api.example.com/v1/products"
#         self.assertEqual(APIUtil.api_endpoint_from_url(another_valid_url), 'products')

#         # Test with invalid URL (no version)
#         invalid_url_no_version = "https://api.example.com/users"
#         self.assertEqual(APIUtil.api_endpoint_from_url(invalid_url_no_version), '')

#         # Test with invalid URL (different format)
#         invalid_url_different_format = "https://example.com/api/users"
#         self.assertEqual(APIUtil.api_endpoint_from_url(invalid_url_different_format), '')

#         # Test with completely incorrect URL format
#         completely_invalid_url = "JustSomeRandomString"
#         self.assertEqual(APIUtil.api_endpoint_from_url(completely_invalid_url), '')

#     async def test_unified_api_call(self):
#         url = "https://api.example.com/v1/test"
#         success_response = {'result': 'Success'}
#         rate_limit_response = {'error': {'message': 'Rate limit exceeded'}}

#         with aioresponses() as m:
#             # Mock a rate limit error followed by a successful response
#             m.post(url, status=429, payload=rate_limit_response)
#             m.post(url, status=200, payload=success_response)

#             response = await APIUtil.unified_api_call(self.session, 'post', url)
#             self.assertEqual(response, success_response)

#             # Ensure that the first call was a rate limit error
#             self.assertTrue(APIUtil.api_rate_limit_error(rate_limit_response))

#     async def test_unified_api_call_with_all_rate_limited(self):
#         url = "https://api.example.com/v1/test"
#         rate_limit_response = {'error': {'message': 'Rate limit exceeded'}}

#         with aioresponses() as m:
#             # Mock three rate limit errors in a row
#             for _ in range(3):
#                 m.post(url, status=429, payload=rate_limit_response)

#             response = await APIUtil.unified_api_call(self.session, 'post', url)
#             self.assertTrue(APIUtil.api_rate_limit_error(response))

#     def test_get_cache_key(self):
#         url = "https://api.example.com/v1/test"
#         params = {"param1": "value1", "param2": "value2"}

#         # Test cache key generation with parameters
#         key_with_params = APIUtil.get_cache_key(url, params)
#         expected_key_with_params = hashlib.md5((url + json.dumps(params, sort_keys=True)).encode('utf-8')).hexdigest()
#         self.assertEqual(key_with_params, expected_key_with_params)

#         # Test cache key generation without parameters
#         key_without_params = APIUtil.get_cache_key(url, None)
#         expected_key_without_params = hashlib.md5(url.encode('utf-8')).hexdigest()
#         self.assertEqual(key_without_params, expected_key_without_params)

#         # Test cache key generation with empty parameters
#         key_with_empty_params = APIUtil.get_cache_key(url, {})
#         self.assertEqual(key_with_empty_params, expected_key_without_params)

#         # Test cache key consistency
#         self.assertEqual(APIUtil.get_cache_key(url, params), key_with_params)

#     async def test_retry_api_call_success(self):
#         url = "https://api.example.com/v1/test"
#         success_response = {'result': 'Success'}

#         with aioresponses() as m:
#             m.get(url, status=200, payload=success_response)

#             response = await APIUtil.retry_api_call(self.session, url)
#             self.assertEqual(response, success_response)

#     async def test_retry_api_call_with_failures(self):
#         url = "https://api.example.com/v1/test"
#         failure_response = {'error': 'Temporary failure'}
#         success_response = {'result': 'Success'}

#         with aioresponses() as m:
#             # First two calls fail, third call succeeds
#             m.get(url, status=500, payload=failure_response)
#             m.get(url, status=500, payload=failure_response)
#             m.get(url, status=200, payload=success_response)

#             response = await APIUtil.retry_api_call(self.session, url, retries=3)
#             self.assertEqual(response, success_response)

#     async def test_retry_api_call_all_failures(self):
#         url = "https://api.example.com/v1/test"
#         failure_response = {'error': 'Temporary failure'}

#         with aioresponses() as m:
#             # All calls fail
#             m.get(url, status=500, payload=failure_response, repeat=3)

#             response = await APIUtil.retry_api_call(self.session, url, retries=3)
#             self.assertIsNone(response)

#     async def test_upload_file_with_retry_success(self):
#         url = "https://api.example.com/v1/upload"
#         success_response = {'result': 'File uploaded successfully'}

#         with aioresponses() as m:
#             m.post(url, status=200, payload=success_response)

#             response = await APIUtil.upload_file_with_retry(self.session, url, self.file_path)
#             self.assertEqual(response, success_response)

#     async def test_upload_file_with_retry_failures(self):
#         url = "https://api.example.com/v1/upload"
#         failure_response = {'error': 'Temporary failure'}

#         with aioresponses() as m:
#             # First two attempts fail, third attempt succeeds
#             m.post(url, status=500, payload=failure_response)
#             m.post(url, status=500, payload=failure_response)
#             m.post(url, status=200, payload={'result': 'File uploaded successfully'})

#             response = await APIUtil.upload_file_with_retry(self.session, url, self.file_path, retries=3)
#             self.assertIsNotNone(response)
#             self.assertEqual(response['result'], 'File uploaded successfully')

#     async def test_get_oauth_token_with_cache_success(self):
#         auth_url = "https://auth.example.com/token"
#         client_id = "client_id"
#         client_secret = "client_secret"
#         scope = "read"
#         token_response = {'access_token': 'mock_access_token'}

#         with aioresponses() as m:
#             m.post(auth_url, status=200, payload=token_response)

#             # Call the method to retrieve the token
#             token = await APIUtil.get_oauth_token_with_cache(self.session, auth_url, client_id, client_secret, scope)
#             self.assertEqual(token, 'mock_access_token')

#             # Call the method again - expecting to use cached value
#             token_cached = await APIUtil.get_oauth_token_with_cache(self.session, auth_url, client_id, client_secret,
#                                                                     scope)
#             self.assertEqual(token_cached, 'mock_access_token')

#     async def test_cached_api_call_success(self):
#         url = "https://api.example.com/v1/data"
#         response_data = {'result': 'Success'}

#         with aioresponses() as m:
#             m.get(url, status=200, payload=response_data)

#             # Call the method to retrieve data
#             response = await APIUtil.cached_api_call(self.session, url)
#             self.assertEqual(response, response_data)

#             # Call the method again - expecting the same result (ideally from cache, but not explicitly tested here)
#             response_cached = await APIUtil.cached_api_call(self.session, url)
#             self.assertEqual(response_cached, response_data)

#     async def test_cached_api_call_failure(self):
#         url = "https://api.example.com/v1/data"

#         with aioresponses() as m:
#             m.get(url, status=500)

#             # Call the method - expecting a failure
#             response = await APIUtil.cached_api_call(self.session, url)
#             self.assertIsNone(response)

# if __name__ == '__main__':
#     unittest.main()
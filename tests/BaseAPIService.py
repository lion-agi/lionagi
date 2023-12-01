import os
import unittest

from lionagi.api.StatusTracker import StatusTracker
from lionagi.api.AsyncQueue import AsyncQueue
from lionagi.api.BaseAPIService import BaseAPIService


class MockAPIService(BaseAPIService):
    async def call_api_endpoint(self):
        pass  # Minimal implementation for testing

    # Optionally, override other methods if specific behavior needs to be tested


class TestBaseAPIService(unittest.TestCase):

    def setUp(self):
        self.api_service = MockAPIService(
            api_key="test_api_key",
            token_encoding_name="test_encoding",
            max_attempts=3,
            status_tracker=StatusTracker(),
            rate_limiter=None,
            queue=AsyncQueue()
        )
        self.test_filename = "test_log.jsonl"

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_handle_error(self):
        error = Exception("Test error")
        payload = {"data": "test"}
        metadata = {"attempt": 1}
        self.api_service.handle_error(error, payload, metadata, self.test_filename)

        self.assertEqual(self.api_service.status_tracker.num_tasks_failed, 1)
        self.assertEqual(self.api_service.status_tracker.num_tasks_in_progress, -1)

        # Check if error is logged correctly
        with open(self.test_filename, "r") as file:
            logged_data = file.readline()
            self.assertIn("Test error", logged_data)
            self.assertIn("test", logged_data)

    def test_api_endpoint_from_url(self):
        test_url = "https://example.com/v1/test_endpoint"
        endpoint = self.api_service.api_endpoint_from_url(test_url)
        self.assertEqual(endpoint, "test_endpoint")

    def test_task_id_generator_function(self):
        id_gen = self.api_service.task_id_generator_function()
        self.assertEqual(next(id_gen), 0)
        self.assertEqual(next(id_gen), 1)

if __name__ == '__main__':
    unittest.main()

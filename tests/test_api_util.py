import os
import unittest
import asyncio

from lionagi.utils.api_util import BaseAPIService, StatusTracker, AsyncQueue, RateLimiter

class MockAPIService(BaseAPIService):
    async def call_api_endpoint(self):
        pass  # Minimal implementation for testing

    # Optionally, override other methods if specific behavior needs to be tested

# class TestBaseAPIService(unittest.TestCase):
#
    # def setUp(self):
    #     self.api_service = MockAPIService(
    #         api_key="test_api_key",
    #         token_encoding_name="test_encoding",
    #         max_attempts=3,
    #         status_tracker=StatusTracker(),
    #         rate_limiter=None,
    #         queue=AsyncQueue()
    #     )
    #     self.test_filename = "test_log.jsonl"
    #
    # def tearDown(self):
    #     if os.path.exists(self.test_filename):
    #         os.remove(self.test_filename)
    #
    # def test_handle_error(self):
    #     error = Exception("Test error")
    #     payload = {"data": "test"}
    #     metadata = {"attempt": 1}
    #     self.api_service.handle_error(error, payload, metadata, self.test_filename)
    #
    #     self.assertEqual(self.api_service.status_tracker.num_tasks_failed, 1)
    #     self.assertEqual(self.api_service.status_tracker.num_tasks_in_progress, -1)
    #
    #     # Check if error is logged correctly
    #     with open(self.test_filename, "r") as file:
    #         logged_data = file.readline()
    #         self.assertIn("Test error", logged_data)
    #         self.assertIn("test", logged_data)
    #
    # def test_api_endpoint_from_url(self):
    #     test_url = "https://example.com/v1/test_endpoint"
    #     endpoint = self.api_service.api_endpoint_from_url(test_url)
    #     self.assertEqual(endpoint, "test_endpoint")
    #
    # def test_task_id_generator_function(self):
    #     id_gen = self.api_service.task_id_generator_function()
    #     self.assertEqual(next(id_gen), 0)
    #     self.assertEqual(next(id_gen), 1)


class TestAsyncQueue(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.queue = AsyncQueue()
        self.results = []

    async def asyncTearDown(self):
        await self.queue.stop()
        # Ensure queue processing has been stopped
        await asyncio.sleep(0.1)

    async def test_queue_processing(self):
        async def dummy_task(item):
            await asyncio.sleep(0.1)
            self.results.append(item)

        processing_task = asyncio.create_task(
            self.queue.process_requests(dummy_task)
        )

        for item in range(5):
            await self.queue.enqueue(item)

        # Signal the end of processing by enqueuing None
        await self.queue.enqueue(None)

        # Wait until the processing task has stopped
        await processing_task

        # Check if all items were processed
        self.assertEqual(self.results, [0, 1, 2, 3, 4])



class MockRateLimiter(RateLimiter):
    def __init__(self, max_requests_per_minute, max_tokens_per_minute):
        super().__init__(max_requests_per_minute, max_tokens_per_minute)

    async def rate_limit_replenisher(self):
        # Replenish logic (simplified for testing)
        await asyncio.sleep(0.1)  # Fast replenish for testing
        self.available_request_capacity = self.max_requests_per_minute
        self.available_token_capacity = self.max_tokens_per_minute

    def calculate_num_token(self, request_details):
        # Simplified token calculation for testing
        return len(request_details)



class TestMockRateLimiter(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.rate_limiter = MockRateLimiter(max_requests_per_minute=100, max_tokens_per_minute=200)

    async def test_rate_limit_replenishment(self):
        self.rate_limiter.available_request_capacity = 0
        self.rate_limiter.available_token_capacity = 0

        await asyncio.sleep(0.2)  # Wait for replenishment to occur

        self.assertEqual(self.rate_limiter.available_request_capacity, 100)
        self.assertEqual(self.rate_limiter.available_token_capacity, 200)

    def test_token_calculation(self):
        request_details = "test_request"
        tokens = self.rate_limiter.calculate_num_token(request_details)

        self.assertEqual(tokens, len(request_details))

class TestStatusTracker(unittest.TestCase):

    def setUp(self):
        self.tracker = StatusTracker()

    def test_task_started(self):
        self.tracker.num_tasks_started += 1
        self.assertEqual(self.tracker.num_tasks_started, 1)

    def test_task_in_progress(self):
        self.tracker.num_tasks_in_progress += 1
        self.assertEqual(self.tracker.num_tasks_in_progress, 1)

    def test_task_succeeded(self):
        self.tracker.num_tasks_succeeded += 1
        self.assertEqual(self.tracker.num_tasks_succeeded, 1)

    def test_task_failed(self):
        self.tracker.num_tasks_failed += 1
        self.assertEqual(self.tracker.num_tasks_failed, 1)

    def test_rate_limit_errors(self):
        self.tracker.num_rate_limit_errors += 1
        self.assertEqual(self.tracker.num_rate_limit_errors, 1)

    def test_api_errors(self):
        self.tracker.num_api_errors += 1
        self.assertEqual(self.tracker.num_api_errors, 1)

    def test_other_errors(self):
        self.tracker.num_other_errors += 1
        self.assertEqual(self.tracker.num_other_errors, 1)

if __name__ == '__main__':
    unittest.main()

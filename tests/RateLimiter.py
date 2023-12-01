import asyncio

from lionagi.api.RateLimiter import RateLimiter


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

import unittest
import asyncio

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

if __name__ == '__main__':
    unittest.main()

import asyncio
import unittest

from lionagi.api.AsyncQueue import AsyncQueue

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

if __name__ == '__main__':
    unittest.main()

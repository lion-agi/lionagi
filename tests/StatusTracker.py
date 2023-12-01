import unittest

from lionagi.api.StatusTracker import StatusTracker


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

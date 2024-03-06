```
from lionagi.libs.ln_api import StatusTracker
```

# StatusTracker

The `StatusTracker` class is a `dataclass` that keeps track of various API task statuses within a system. 

## Attributes

- `num_tasks_started`: The number of tasks that have been initiated.
- `num_tasks_in_progress`: The number of tasks currently being processed.
- `num_tasks_succeeded`: The number of tasks that have completed successfully.
- `num_tasks_failed`: The number of tasks that have failed.
- `num_rate_limit_errors`: The number of tasks that failed due to rate limiting.
- `num_api_errors`: The number of tasks that failed due to API errors.
- `num_other_errors`: The number of tasks that failed due to other errors.

Examples:
```python
tracker = StatusTracker()
tracker.num_tasks_started += 1
tracker.num_tasks_in_progress += 1
# Perform the task
tracker.num_tasks_in_progress -= 1
tracker.num_tasks_succeeded += 1

tracker.num_tasks_started += 1
tracker.num_tasks_in_progress += 1
# Perform the task
tracker.num_tasks_in_progress -= 1
tracker.num_tasks_failed += 1
tracker.num_rate_limit_errors += 1
```


*(borrowed from [OpenAI cookbook](https://github.com/openai/openai-cookbook/blob/main/examples/api_request_parallel_processor.py))


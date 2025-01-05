# Rate Limited Processor API Reference

## Overview

The Rate Limited Processor provides request flow control for API calls by managing:
- Maximum request rates (requests per minute)
- Token usage limits (tokens per minute)
- Request queueing and execution
- Automatic capacity refresh cycles

## RateLimitedAPIProcessor

Base processor implementing rate limiting logic.

```python
class RateLimitedAPIProcessor(Processor):
    """Rate-limited request processor with token tracking."""

    def __init__(
        self,
        queue_capacity: int,
        capacity_refresh_time: float,
        interval: float | None = None,
        limit_requests: int | None = None,
        limit_tokens: int | None = None,
    ) -> None:
        """
        Initialize processor with rate limits.
        
        Args:
            queue_capacity: Maximum requests in queue
            capacity_refresh_time: Seconds between limit resets
            interval: Custom processing interval (default: refresh_time)
            limit_requests: Max requests per refresh cycle
            limit_tokens: Max tokens per refresh cycle
        """
```

### Key Methods

```python
async def request_permission(self, required_tokens: int = None) -> bool:
    """Check if request can proceed under current limits.
    
    A request is allowed if:
    1. Queue has available capacity, and
    2. Under request limit (if set), and
    3. Under token limit (if set and tokens provided)
    """

async def start_replenishing(self) -> None:
    """Begin capacity refresh cycle.
    
    On each cycle:
    1. Wait for interval
    2. Reset available request count
    3. Reset available token count
    """

@classmethod
async def create(cls, queue_capacity: int, capacity_refresh_time: float, **kwargs) -> Self:
    """Create and start a processor instance."""
```

## RateLimitedAPIExecutor 

High-level executor coordinating API requests with rate limiting.

```python
class RateLimitedAPIExecutor(Executor):
    """
    Manages rate-limited API request execution.
    
    Key features:
    - Request queuing and scheduling
    - Rate limit enforcement
    - Token usage tracking
    - Response collection
    """
```

### Usage Pattern

```python
# Initialize with rate limits
executor = RateLimitedAPIExecutor(
    queue_capacity=100,     # Max queued requests
    capacity_refresh_time=60,  # 1-minute refresh
    limit_requests=50,      # 50 RPM
    limit_tokens=10000      # 10K TPM
)

# Start processor
await executor.start()

# Queue and process requests
await executor.append(api_call)  # Add to queue
await executor.forward()         # Process queue

# Get results from completed events
if api_call.id in executor.completed_events:
    result = executor.pile.pop(api_call.id)
```

## Rate Limiting Strategy

The processor maintains separate counters for requests and tokens:

1. Request Limiting:
   - Tracks requests/minute using counter
   - Resets on refresh cycle
   - Rejects when limit reached

2. Token Limiting:
   - Tracks token usage via TokenCalculator
   - Considers both input and expected output
   - Resets available tokens on cycle

3. Queue Management:
   - FIFO request processing
   - Request permission checks before execution
   - Automatic requeuing on rate limit hits

4. Refresh Cycle:
   - Resets counters on interval
   - Processes queued requests when capacity available
   - Maintains continuous operation

## Error Handling

The processor handles several error cases:

1. Rate Limit Exceeded
   - Requests queued for next cycle
   - Token limits enforced pre-execution
   - Gradual request processing

2. Processor Shutdown
   - Graceful task cancellation
   - Queue cleanup
   - Error status for pending requests

# LionAGI Cookbook

## Chapter 11: Building a High-Performance Service

In previous chapters, you built various systems. Now we'll explore performance optimization by building a high-volume service that:
- Handles concurrent requests
- Manages resources efficiently
- Monitors performance
- Scales dynamically

### Prerequisites
- Completed [Chapter 10](ch10_e2e_project.md)
- Understanding of async programming
- Basic Python knowledge

## Performance Basics

### Resource Management
```python
from lionagi import (
    Branch, Model, Session,
    RateLimitedAPIExecutor,
    types
)
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import asyncio
import json
import psutil

class ResourceManager:
    """Manage system resources."""
    def __init__(
        self,
        requests_per_minute: int = 60,
        max_tokens: int = 100000,
        queue_size: int = 1000
    ):
        # Create executor
        self.executor = RateLimitedAPIExecutor(
            queue_capacity=queue_size,
            capacity_refresh_time=60,
            limit_requests=requests_per_minute,
            limit_tokens=max_tokens
        )
        
        # Track resources
        self.usage: List[dict] = []
        self.start_time = datetime.now()
    
    def get_usage(self) -> dict:
        """Get current resource usage."""
        return {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "timestamp": datetime.now().isoformat()
        }
    
    def track_usage(self):
        """Track resource usage."""
        usage = self.get_usage()
        self.usage.append(usage)
        
        # Keep last hour
        cutoff = datetime.now().timestamp() - 3600
        self.usage = [
            u for u in self.usage
            if datetime.fromisoformat(u["timestamp"]).timestamp() > cutoff
        ]
    
    def get_stats(self) -> dict:
        """Get resource statistics."""
        if not self.usage:
            return {}
        
        return {
            "uptime": (datetime.now() - self.start_time).seconds,
            "cpu_avg": sum(u["cpu"] for u in self.usage) / len(self.usage),
            "memory_avg": sum(u["memory"] for u in self.usage) / len(self.usage),
            "disk_avg": sum(u["disk"] for u in self.usage) / len(self.usage)
        }

class PerformanceMonitor:
    """Monitor system performance."""
    def __init__(self):
        self.requests: List[dict] = []
        self.errors: List[dict] = []
        self.start_time = datetime.now()
    
    def track_request(
        self,
        request_id: str,
        duration: float,
        error: str = None
    ):
        """Track request performance."""
        record = {
            "id": request_id,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        if error:
            record["error"] = error
            self.errors.append(record)
        else:
            self.requests.append(record)
        
        # Keep last hour
        cutoff = datetime.now().timestamp() - 3600
        self.requests = [
            r for r in self.requests
            if datetime.fromisoformat(r["timestamp"]).timestamp() > cutoff
        ]
        self.errors = [
            e for e in self.errors
            if datetime.fromisoformat(e["timestamp"]).timestamp() > cutoff
        ]
    
    def get_stats(self) -> dict:
        """Get performance statistics."""
        total_requests = len(self.requests) + len(self.errors)
        if not total_requests:
            return {}
        
        return {
            "uptime": (datetime.now() - self.start_time).seconds,
            "total_requests": total_requests,
            "error_rate": len(self.errors) / total_requests,
            "avg_duration": sum(
                r["duration"] for r in self.requests
            ) / len(self.requests) if self.requests else 0
        }
```

### Queue Management
```python
class RequestQueue:
    """Manage request queue."""
    def __init__(
        self,
        max_size: int = 1000,
        workers: int = 4
    ):
        # Create queues
        self.pending = asyncio.Queue(maxsize=max_size)
        self.processing = set()
        self.completed = []
        
        # Worker settings
        self.max_workers = workers
        self.current_workers = 0
    
    async def add_request(
        self,
        request: dict
    ) -> bool:
        """Add request to queue."""
        try:
            await self.pending.put(request)
            return True
        except asyncio.QueueFull:
            return False
    
    async def process_request(
        self,
        processor: callable
    ):
        """Process single request."""
        while True:
            try:
                # Get request
                request = await self.pending.get()
                self.processing.add(request["id"])
                
                # Process request
                try:
                    result = await processor(request)
                    self.completed.append({
                        "request": request,
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    self.completed.append({
                        "request": request,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Update tracking
                self.processing.remove(request["id"])
                self.pending.task_done()
            
            except asyncio.CancelledError:
                break
    
    async def start_workers(
        self,
        processor: callable
    ):
        """Start worker tasks."""
        workers = []
        for _ in range(self.max_workers):
            worker = asyncio.create_task(
                self.process_request(processor)
            )
            workers.append(worker)
            self.current_workers += 1
        
        return workers
    
    def get_stats(self) -> dict:
        """Get queue statistics."""
        return {
            "pending": self.pending.qsize(),
            "processing": len(self.processing),
            "completed": len(self.completed),
            "workers": self.current_workers
        }
```

## Advanced Features

### Dynamic Scaling
```python
class ScalableService:
    """Service with dynamic scaling."""
    def __init__(
        self,
        name: str = "Service",
        save_dir: str = "service",
        min_workers: int = 2,
        max_workers: int = 8
    ):
        # Create components
        self.resources = ResourceManager(
            requests_per_minute=120,  # 2 requests/second
            queue_size=2000
        )
        
        self.monitor = PerformanceMonitor()
        
        self.queue = RequestQueue(
            max_size=2000,
            workers=min_workers
        )
        
        # Scaling settings
        self.min_workers = min_workers
        self.max_workers = max_workers
        
        # Setup storage
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Track service
        self.stats: List[dict] = []
    
    async def handle_request(
        self,
        request: dict
    ) -> dict:
        """Handle service request."""
        try:
            # Add to queue
            if not await self.queue.add_request(request):
                return {
                    "status": "error",
                    "error": "Queue full"
                }
            
            # Track request
            start = datetime.now()
            
            # Wait for completion
            while True:
                # Check completion
                for record in self.queue.completed:
                    if record["request"]["id"] == request["id"]:
                        # Track performance
                        duration = (
                            datetime.now() - start
                        ).total_seconds()
                        
                        self.monitor.track_request(
                            request["id"],
                            duration,
                            record.get("error")
                        )
                        
                        # Return result
                        if "error" in record:
                            return {
                                "status": "error",
                                "error": record["error"]
                            }
                        else:
                            return {
                                "status": "success",
                                "result": record["result"]
                            }
                
                # Check timeout
                if (datetime.now() - start).seconds > 30:
                    return {
                        "status": "error",
                        "error": "Request timeout"
                    }
                
                await asyncio.sleep(0.1)
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def monitor_performance(self):
        """Monitor system performance."""
        while True:
            # Track resources
            self.resources.track_usage()
            
            # Get statistics
            stats = {
                "resources": self.resources.get_stats(),
                "performance": self.monitor.get_stats(),
                "queue": self.queue.get_stats(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Save stats
            self.stats.append(stats)
            
            # Keep last day
            cutoff = datetime.now().timestamp() - 86400
            self.stats = [
                s for s in self.stats
                if datetime.fromisoformat(s["timestamp"]).timestamp() > cutoff
            ]
            
            # Scale workers
            await self.scale_workers()
            
            await asyncio.sleep(60)
    
    async def scale_workers(self):
        """Scale workers based on load."""
        if not self.stats:
            return
        
        # Get latest stats
        stats = self.stats[-1]
        
        # Check CPU usage
        if stats["resources"]["cpu_avg"] > 80:
            # Scale down if high CPU
            target = max(
                self.min_workers,
                self.queue.current_workers - 1
            )
        elif stats["queue"]["pending"] > 100:
            # Scale up if high queue
            target = min(
                self.max_workers,
                self.queue.current_workers + 1
            )
        else:
            # Maintain current
            target = self.queue.current_workers
        
        # Adjust workers
        while self.queue.current_workers != target:
            if self.queue.current_workers < target:
                # Add worker
                workers = await self.queue.start_workers(
                    self.process_request
                )
                self.workers.extend(workers)
            else:
                # Remove worker
                worker = self.workers.pop()
                worker.cancel()
                self.queue.current_workers -= 1
    
    async def start(self):
        """Start service."""
        # Start workers
        self.workers = await self.queue.start_workers(
            self.process_request
        )
        
        # Start monitoring
        self.monitor_task = asyncio.create_task(
            self.monitor_performance()
        )
    
    async def stop(self):
        """Stop service."""
        # Cancel workers
        for worker in self.workers:
            worker.cancel()
        
        # Cancel monitoring
        self.monitor_task.cancel()
        
        # Save final stats
        stats_file = self.save_dir / "final_stats.json"
        with open(stats_file, "w") as f:
            json.dump(self.stats, f, indent=2)

# Usage
async def run_service():
    """Demo scalable service."""
    # Create service
    service = ScalableService(
        name="HighPerformance",
        save_dir="service_data"
    )
    
    # Start service
    await service.start()
    
    try:
        # Send requests
        requests = [
            {
                "id": f"req_{i}",
                "type": "process",
                "data": f"Data {i}"
            }
            for i in range(100)
        ]
        
        # Process concurrently
        tasks = [
            service.handle_request(request)
            for request in requests
        ]
        
        results = await asyncio.gather(*tasks)
        print("\nResults:", results)
        
        # Show stats
        print("\nFinal Stats:", service.stats[-1])
    
    finally:
        # Stop service
        await service.stop()

# Run service
asyncio.run(run_service())
```

## Best Practices

1. **Resource Management**
   - Monitor usage
   - Set proper limits
   - Handle bursts
   - Scale appropriately

2. **Queue Management**
   - Handle backpressure
   - Process efficiently
   - Track progress
   - Handle timeouts

3. **Performance Monitoring**
   - Track metrics
   - Analyze patterns
   - Alert issues
   - Optimize bottlenecks

## Quick Reference
```python
from lionagi import RateLimitedAPIExecutor

# Create executor
executor = RateLimitedAPIExecutor(
    queue_capacity=1000,
    capacity_refresh_time=60,
    limit_requests=60
)

# Create queue
queue = asyncio.Queue(maxsize=1000)

# Process requests
while True:
    request = await queue.get()
    try:
        await process(request)
    finally:
        queue.task_done()
```

## Next Steps

You've learned:
- How to manage resources
- How to handle queues
- How to monitor performance
- How to scale services

In [Chapter 12](ch12_graph.md), we'll explore graph-based operations for complex relationships.

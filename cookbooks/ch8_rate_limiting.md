# LionAGI Cookbook

## Chapter 8: Building a Data Processing Service

In previous chapters, you built various systems. Now we'll explore rate limiting by building a data processing service that:
- Handles high request volume
- Manages API rate limits
- Processes data efficiently
- Scales with demand

### Prerequisites
- Completed [Chapter 7](ch7_multi_agent.md)
- Understanding of async programming
- Basic Python knowledge

## Rate Limiting Basics

### Basic Setup
```python
from lionagi import Branch, Model, RateLimitedAPIExecutor, types
from datetime import datetime
from pathlib import Path
import asyncio
import json

class ProcessingService:
    """Rate-limited processing service."""
    def __init__(
        self,
        name: str = "DataProcessor",
        save_dir: str = "processing",
        requests_per_minute: int = 60,
        max_tokens: int = 100000
    ):
        # Create executor
        self.executor = RateLimitedAPIExecutor(
            queue_capacity=1000,
            capacity_refresh_time=60,
            limit_requests=requests_per_minute,
            limit_tokens=max_tokens
        )
        
        # Create processor
        self.processor = Branch(
            name=name,
            system="""You are a data processor.
            Process data efficiently.
            Follow data schemas.
            Ensure data quality."""
        )
        
        # Configure model
        self.model = Model(
            provider="openai",
            model="gpt-3.5-turbo",
            temperature=0.3,  # More precise
            executor=self.executor  # Use rate limiter
        )
        self.processor.add_model(self.model)
        
        # Setup storage
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Track requests
        self.requests: dict[str, dict] = {}
        self._load_requests()
    
    def _load_requests(self):
        """Load saved requests."""
        for file in self.save_dir.glob("*.json"):
            with open(file) as f:
                request = json.load(f)
                self.requests[request["id"]] = request
    
    async def process_data(
        self,
        data: dict,
        schema: dict = None
    ) -> dict:
        """Process data with rate limiting."""
        try:
            # Create request
            request_id = f"req_{len(self.requests)}"
            request = {
                "id": request_id,
                "data": data,
                "schema": schema,
                "status": "received",
                "timestamp": datetime.now().isoformat()
            }
            
            # Save request
            self.requests[request_id] = request
            
            # Process data
            prompt = f"""Process data following schema:
            Data: {data}
            Schema: {schema or 'No schema provided'}"""
            
            result = await self.processor.chat(prompt)
            
            # Update request
            request["result"] = result
            request["status"] = "completed"
            request["completed"] = datetime.now().isoformat()
            
            # Save result
            file_path = self.save_dir / f"{request_id}.json"
            with open(file_path, "w") as f:
                json.dump(request, f, indent=2)
            
            return {
                "status": "success",
                "request_id": request_id,
                "result": result
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_request(
        self,
        request_id: str
    ) -> dict:
        """Get request details."""
        return self.requests.get(request_id, {
            "error": f"Unknown request: {request_id}"
        })

# Usage
async def process_items():
    """Demo data processing."""
    # Create service
    service = ProcessingService(
        name="DataService",
        requests_per_minute=60
    )
    
    # Process items
    items = [
        {
            "text": "Process this text",
            "type": "text",
            "options": {
                "format": "json",
                "fields": ["sentiment", "topics"]
            }
        },
        {
            "numbers": [1, 2, 3, 4, 5],
            "type": "numeric",
            "options": {
                "stats": ["mean", "std"],
                "format": "json"
            }
        }
    ]
    
    # Process each item
    results = []
    for item in items:
        result = await service.process_data(
            data=item,
            schema={
                "type": "object",
                "properties": {
                    "processed": {"type": "object"},
                    "metadata": {"type": "object"}
                }
            }
        )
        results.append(result)
        print(f"\nProcessed item: {result}")
    
    return results

# Run processing
asyncio.run(process_items())
```

## Advanced Processing

### Batch Processing
```python
class BatchProcessor:
    """Rate-limited batch processor."""
    def __init__(
        self,
        name: str = "BatchProcessor",
        save_dir: str = "batches",
        batch_size: int = 10,
        requests_per_minute: int = 60
    ):
        # Create service
        self.service = ProcessingService(
            name=name,
            save_dir=save_dir,
            requests_per_minute=requests_per_minute
        )
        
        # Batch settings
        self.batch_size = batch_size
        self.batches: dict[str, dict] = {}
    
    async def process_batch(
        self,
        items: list[dict],
        schema: dict = None
    ) -> dict:
        """Process batch of items."""
        try:
            # Create batch
            batch_id = f"batch_{len(self.batches)}"
            batch = {
                "id": batch_id,
                "items": items,
                "schema": schema,
                "status": "processing",
                "timestamp": datetime.now().isoformat()
            }
            
            # Process in chunks
            results = []
            for i in range(0, len(items), self.batch_size):
                chunk = items[i:i + self.batch_size]
                
                # Process chunk concurrently
                tasks = [
                    self.service.process_data(
                        data=item,
                        schema=schema
                    )
                    for item in chunk
                ]
                
                # Wait for all items
                chunk_results = await asyncio.gather(*tasks)
                results.extend(chunk_results)
            
            # Update batch
            batch["results"] = results
            batch["status"] = "completed"
            batch["completed"] = datetime.now().isoformat()
            
            # Save batch
            self.batches[batch_id] = batch
            
            return {
                "status": "success",
                "batch_id": batch_id,
                "results": results
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_batch(
        self,
        batch_id: str
    ) -> dict:
        """Get batch details."""
        return self.batches.get(batch_id, {
            "error": f"Unknown batch: {batch_id}"
        })

# Usage
async def process_batch():
    """Demo batch processing."""
    # Create processor
    processor = BatchProcessor(
        name="BatchService",
        batch_size=5,
        requests_per_minute=60
    )
    
    # Create items
    items = [
        {"text": f"Process text {i}", "type": "text"}
        for i in range(20)
    ]
    
    # Process batch
    result = await processor.process_batch(
        items=items,
        schema={
            "type": "object",
            "properties": {
                "processed": {"type": "string"},
                "metadata": {"type": "object"}
            }
        }
    )
    print("\nBatch result:", result)
    
    return result

# Run batch
asyncio.run(process_batch())
```

## Real-World Example

### Processing Pipeline
```python
from lionagi import Branch, Model, RateLimitedAPIExecutor, types
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import asyncio
import json

class ProcessingStage(Form):
    """Processing stage configuration."""
    name: str = Field(
        description="Stage name"
    )
    type: str = Field(
        description="Processing type",
        pattern="^(text|numeric|mixed)$"
    )
    options: Dict[str, Any] = Field(
        description="Processing options"
    )
    schema: Dict[str, Any] = Field(
        description="Output schema"
    )
    rate_limit: int = Field(
        description="Requests per minute",
        ge=1
    )

class Pipeline:
    """Complete processing pipeline."""
    def __init__(
        self,
        name: str = "Pipeline",
        save_dir: str = "pipeline"
    ):
        # Setup storage
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Track stages
        self.stages: Dict[str, dict] = {}
        self.processors: Dict[str, ProcessingService] = {}
        self.results: Dict[str, dict] = {}
    
    async def add_stage(
        self,
        config: dict
    ) -> dict:
        """Add processing stage."""
        try:
            # Validate config
            stage = ProcessingStage(**config)
            
            # Create processor
            processor = ProcessingService(
                name=f"{stage.name}Processor",
                save_dir=f"{self.save_dir}/{stage.name}",
                requests_per_minute=stage.rate_limit
            )
            
            # Record stage
            stage_id = f"stage_{len(self.stages)}"
            self.stages[stage_id] = stage.model_dump()
            self.processors[stage_id] = processor
            
            return {
                "status": "success",
                "stage_id": stage_id
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def process_data(
        self,
        data: list[dict]
    ) -> dict:
        """Process data through pipeline."""
        try:
            # Create job
            job_id = f"job_{len(self.results)}"
            job = {
                "id": job_id,
                "data": data,
                "stages": [],
                "status": "processing",
                "timestamp": datetime.now().isoformat()
            }
            
            # Process each stage
            current_data = data
            for stage_id, stage in self.stages.items():
                print(f"\nProcessing stage: {stage['name']}")
                
                # Process batch
                processor = self.processors[stage_id]
                result = await processor.process_data(
                    data=current_data,
                    schema=stage["schema"]
                )
                
                # Record stage
                job["stages"].append({
                    "stage_id": stage_id,
                    "result": result
                })
                
                # Update data for next stage
                if result["status"] == "success":
                    current_data = result["result"]
                else:
                    return {
                        "status": "error",
                        "stage": stage["name"],
                        "error": result["error"]
                    }
            
            # Complete job
            job["status"] = "completed"
            job["completed"] = datetime.now().isoformat()
            
            # Save results
            self.results[job_id] = job
            
            return {
                "status": "success",
                "job_id": job_id,
                "results": job
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_results(
        self,
        job_id: str
    ) -> dict:
        """Get job results."""
        return self.results.get(job_id, {
            "error": f"Unknown job: {job_id}"
        })

# Usage
async def run_pipeline():
    """Demo processing pipeline."""
    # Create pipeline
    pipeline = Pipeline(
        name="DataPipeline",
        save_dir="pipeline_data"
    )
    
    # Add stages
    stages = [
        {
            "name": "TextProcessor",
            "type": "text",
            "options": {
                "extract": ["entities", "sentiment"],
                "format": "json"
            },
            "schema": {
                "type": "object",
                "properties": {
                    "entities": {"type": "array"},
                    "sentiment": {"type": "string"}
                }
            },
            "rate_limit": 60
        },
        {
            "name": "DataEnricher",
            "type": "mixed",
            "options": {
                "enrich": ["categories", "metadata"],
                "format": "json"
            },
            "schema": {
                "type": "object",
                "properties": {
                    "enriched": {"type": "object"},
                    "metadata": {"type": "object"}
                }
            },
            "rate_limit": 30
        }
    ]
    
    # Add each stage
    for stage in stages:
        result = await pipeline.add_stage(stage)
        print(f"\nAdded stage: {result}")
    
    # Process data
    data = [
        {
            "text": "Process this text",
            "metadata": {"source": "user"}
        },
        {
            "text": "Another text to process",
            "metadata": {"source": "system"}
        }
    ]
    
    # Run pipeline
    result = await pipeline.process_data(data)
    print("\nPipeline result:", result)
    
    return result

# Run pipeline
asyncio.run(run_pipeline())
```

## Best Practices

1. **Rate Limiting**
   - Set appropriate limits
   - Handle bursts
   - Monitor usage
   - Scale dynamically

2. **Queue Management**
   - Handle backpressure
   - Process in batches
   - Monitor queue size
   - Handle timeouts

3. **Error Handling**
   - Retry with backoff
   - Handle failures
   - Log errors
   - Monitor health

## Quick Reference
```python
from lionagi import Branch, Model, RateLimitedAPIExecutor

# Create executor
executor = RateLimitedAPIExecutor(
    queue_capacity=1000,
    capacity_refresh_time=60,
    limit_requests=60,
    limit_tokens=100000
)

# Create model
model = Model(
    provider="openai",
    executor=executor
)

# Create processor
processor = Branch(name="Processor")
processor.add_model(model)

# Process with rate limiting
result = await processor.chat("Process data")
```

## Next Steps

You've learned:
- How to implement rate limiting
- How to process batches
- How to manage queues
- How to handle scaling

In [Chapter 9](ch9_data_adapter.md), we'll explore data adapters for format conversion.

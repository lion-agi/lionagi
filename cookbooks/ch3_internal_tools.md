# LionAGI Cookbook

## Chapter 3: Building a Data Processing Assistant

In previous chapters, you built a research assistant and customer service bot. Now we'll explore function calling by building a data processing assistant that:
- Processes CSV and JSON files
- Validates data formats
- Generates reports
- Handles errors gracefully

### Prerequisites
- Completed [Chapter 2](ch2_concepts.md)
- Basic Python knowledge
- Understanding of data formats

## Function Calling

### Basic Tools
```python
from lionagi import Branch, Model, Tool, types
import pandas as pd
from pathlib import Path

# Define tools
def read_csv(
    filepath: str,
    encoding: str = "utf-8"
) -> dict:
    """Read CSV file into DataFrame."""
    try:
        df = pd.read_csv(filepath, encoding=encoding)
        return {
            "data": df.to_dict(orient="records"),
            "columns": df.columns.tolist(),
            "rows": len(df)
        }
    except Exception as e:
        return {"error": str(e)}

def validate_data(
    data: list[dict],
    required: list[str]
) -> dict:
    """Validate data fields."""
    missing = []
    for row in data:
        for field in required:
            if field not in row:
                missing.append(field)
    
    return {
        "valid": len(missing) == 0,
        "missing": list(set(missing))
    }

def generate_summary(
    data: list[dict]
) -> dict:
    """Generate data summary."""
    if not data:
        return {"error": "No data provided"}
    
    # Get fields
    fields = list(data[0].keys())
    
    # Analyze each field
    summary = {}
    for field in fields:
        values = [row[field] for row in data]
        summary[field] = {
            "type": type(values[0]).__name__,
            "unique": len(set(values)),
            "missing": values.count(None)
        }
    
    return summary

# Create tools
tools = [
    Tool(func=read_csv),
    Tool(func=validate_data),
    Tool(func=generate_summary)
]
```

### Tool Integration
```python
class DataAssistant:
    """Data processing assistant."""
    def __init__(
        self,
        name: str = "DataAssistant",
        model: str = "gpt-3.5-turbo"
    ):
        # Create assistant
        self.assistant = Branch(
            name=name,
            system="""You are a data processing assistant.
            Help users analyze and validate data.
            Use available tools appropriately.
            Explain your findings clearly."""
        )
        
        # Configure model
        self.model = Model(
            provider="openai",
            model=model,
            temperature=0.3  # More precise for data tasks
        )
        self.assistant.add_model(self.model)
        
        # Add tools
        for tool in tools:
            self.assistant.add_tool(tool)
    
    async def process_file(
        self,
        filepath: str,
        required_fields: list[str] = None
    ) -> dict:
        """Process data file."""
        try:
            # Read file
            data = await self.assistant.use_tool(
                "read_csv",
                filepath=filepath
            )
            
            if "error" in data:
                return data
            
            # Validate if needed
            results = {"data": data}
            if required_fields:
                validation = await self.assistant.use_tool(
                    "validate_data",
                    data=data["data"],
                    required=required_fields
                )
                results["validation"] = validation
            
            # Generate summary
            summary = await self.assistant.use_tool(
                "generate_summary",
                data=data["data"]
            )
            results["summary"] = summary
            
            return results
        
        except Exception as e:
            return {"error": str(e)}
    
    async def analyze_data(
        self,
        data: dict
    ) -> str:
        """Get AI analysis of data."""
        if "error" in data:
            return f"Error analyzing data: {data['error']}"
        
        prompt = f"""
        Analyze this data:
        
        Summary: {data['summary']}
        
        Validation: {data.get('validation', 'Not performed')}
        
        Consider:
        - Data quality
        - Missing values
        - Field types
        - Potential issues
        """
        
        try:
            return await self.assistant.chat(prompt)
        except Exception as e:
            return f"Error getting analysis: {str(e)}"

# Usage
async def process_data():
    """Demo data processing."""
    # Create assistant
    assistant = DataAssistant(
        name="DataAnalyst",
        model="gpt-4"  # Better for analysis
    )
    
    # Process sample file
    results = await assistant.process_file(
        filepath="data/users.csv",
        required_fields=["id", "name", "email"]
    )
    
    # Get analysis
    analysis = await assistant.analyze_data(results)
    
    print("Results:", results)
    print("\nAnalysis:", analysis)
```

### Error Recovery
```python
class ResilientDataAssistant(DataAssistant):
    """Data assistant with error recovery."""
    async def process_file(
        self,
        filepath: str,
        required_fields: list[str] = None,
        retries: int = 3
    ) -> dict:
        """Process file with retries."""
        attempts = 0
        while attempts < retries:
            try:
                return await super().process_file(
                    filepath,
                    required_fields
                )
            except Exception as e:
                attempts += 1
                if attempts == retries:
                    return {
                        "error": str(e),
                        "attempts": attempts
                    }
                # Wait before retry
                await asyncio.sleep(2 ** attempts)
    
    async def safe_tool_call(
        self,
        tool: str,
        retries: int = 3,
        **kwargs
    ) -> dict:
        """Call tool with error recovery."""
        attempts = 0
        while attempts < retries:
            try:
                return await self.assistant.use_tool(
                    tool,
                    **kwargs
                )
            except Exception as e:
                attempts += 1
                if attempts == retries:
                    return {
                        "error": str(e),
                        "tool": tool,
                        "attempts": attempts
                    }
                await asyncio.sleep(2 ** attempts)
```

## Real-World Example

### Data Pipeline
```python
from lionagi import Branch, Model, Tool, types
from pathlib import Path
import json
import pandas as pd

class DataPipeline:
    """Complete data processing pipeline."""
    def __init__(
        self,
        input_dir: str = "data/input",
        output_dir: str = "data/output",
        required_fields: list[str] = None
    ):
        # Setup assistant
        self.assistant = ResilientDataAssistant(
            name="DataPipeline",
            model="gpt-4"
        )
        
        # Setup directories
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.required_fields = required_fields or []
    
    async def process_directory(
        self
    ) -> dict:
        """Process all files in directory."""
        results = {}
        
        # Process each file
        for file in self.input_dir.glob("*.csv"):
            print(f"\nProcessing: {file.name}")
            
            try:
                # Process file
                data = await self.assistant.process_file(
                    str(file),
                    self.required_fields
                )
                
                # Get analysis
                analysis = await self.assistant.analyze_data(
                    data
                )
                
                # Save results
                output = {
                    "data": data,
                    "analysis": analysis,
                    "timestamp": datetime.now().isoformat()
                }
                
                output_file = self.output_dir / f"{file.stem}_results.json"
                with open(output_file, "w") as f:
                    json.dump(output, f, indent=2)
                
                results[file.name] = {
                    "status": "success",
                    "output": str(output_file)
                }
            
            except Exception as e:
                results[file.name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    async def generate_report(
        self
    ) -> str:
        """Generate pipeline report."""
        # Get all results
        results = []
        for file in self.output_dir.glob("*_results.json"):
            with open(file) as f:
                results.append(json.load(f))
        
        # Generate report
        prompt = f"""
        Generate data pipeline report.
        
        Files processed: {len(results)}
        Results: {json.dumps(results, indent=2)}
        
        Include:
        - Overall data quality
        - Common issues
        - Recommendations
        - Next steps
        """
        
        try:
            return await self.assistant.assistant.chat(prompt)
        except Exception as e:
            return f"Error generating report: {str(e)}"

# Usage
async def run_pipeline():
    """Run data pipeline."""
    # Create pipeline
    pipeline = DataPipeline(
        input_dir="data/raw",
        output_dir="data/processed",
        required_fields=["id", "name", "email"]
    )
    
    # Process files
    results = await pipeline.process_directory()
    print("\nProcessing Results:", results)
    
    # Generate report
    report = await pipeline.generate_report()
    print("\nPipeline Report:", report)
    
    # Save report
    report_file = pipeline.output_dir / "pipeline_report.txt"
    with open(report_file, "w") as f:
        f.write(report)

# Run pipeline
asyncio.run(run_pipeline())
```

## Best Practices

1. **Tool Design**
   - Keep tools focused
   - Handle errors properly
   - Validate inputs
   - Return clear results

2. **Error Recovery**
   - Use retries wisely
   - Handle timeouts
   - Log failures
   - Clean up resources

3. **Pipeline Design**
   - Process incrementally
   - Save results
   - Generate reports
   - Monitor progress

## Quick Reference
```python
from lionagi import Branch, Model, Tool, types

# Create tool
def process_data(data: dict) -> dict:
    """Process data safely."""
    try:
        # Processing logic
        return {"result": "success"}
    except Exception as e:
        return {"error": str(e)}

# Create assistant
assistant = Branch(name="DataProcessor")
model = Model(provider="openai")
assistant.add_model(model)

# Add tool
tool = Tool(func=process_data)
assistant.add_tool(tool)

# Use tool
try:
    result = await assistant.use_tool(
        "process_data",
        data={"key": "value"}
    )
    print(result)
except Exception as e:
    print(f"Error: {str(e)}")
```

## Next Steps

You've learned:
- How to create and use tools
- How to build data pipelines
- How to handle errors
- How to generate reports

In [Chapter 4](ch4_structured_forms.md), we'll explore forms for structured data handling.

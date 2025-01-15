# LionAGI Cookbook

## Chapter 9: Building a Data Integration System

In previous chapters, you built various systems. Now we'll explore data adapters by building a data integration system that:
- Converts between formats
- Validates data structures
- Transforms content
- Handles integrations

### Prerequisites
- Completed [Chapter 8](ch8_rate_limiting.md)
- Understanding of data formats
- Basic Python knowledge

## Adapter Basics

### Basic Adapters
```python
from lionagi import Branch, Model, types
from lionagi.protocols.adapters import (
    JsonAdapter,
    JsonFileAdapter,
    CSVFileAdapter,
    ExcelFileAdapter
)
from pathlib import Path
import json
import pandas as pd

class DataConverter:
    """Basic data converter."""
    def __init__(
        self,
        save_dir: str = "conversions"
    ):
        # Setup storage
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Register adapters
        self.adapters = {
            ".json": JsonFileAdapter,
            ".csv": CSVFileAdapter,
            ".xlsx": ExcelFileAdapter
        }
        
        # Track conversions
        self.conversions: dict[str, dict] = {}
    
    def convert_file(
        self,
        source: str,
        target: str,
        schema: dict = None
    ) -> dict:
        """Convert file between formats."""
        try:
            # Get extensions
            source_ext = Path(source).suffix
            target_ext = Path(target).suffix
            
            # Validate formats
            if source_ext not in self.adapters:
                return {
                    "status": "error",
                    "error": f"Unsupported source: {source_ext}"
                }
            
            if target_ext not in self.adapters:
                return {
                    "status": "error",
                    "error": f"Unsupported target: {target_ext}"
                }
            
            # Load data
            source_adapter = self.adapters[source_ext]
            data = source_adapter.from_obj(
                dict,
                source,
                many=True
            )
            
            # Validate if needed
            if schema:
                # Basic validation
                for item in data:
                    for field, type_ in schema.items():
                        if field not in item:
                            return {
                                "status": "error",
                                "error": f"Missing field: {field}"
                            }
                        
                        if not isinstance(item[field], type_):
                            return {
                                "status": "error",
                                "error": f"Invalid type for {field}"
                            }
            
            # Save conversion
            target_adapter = self.adapters[target_ext]
            target_adapter.to_obj(
                data,
                fp=target,
                many=True
            )
            
            # Record conversion
            conversion_id = f"conv_{len(self.conversions)}"
            conversion = {
                "id": conversion_id,
                "source": source,
                "target": target,
                "schema": schema,
                "items": len(data)
            }
            
            self.conversions[conversion_id] = conversion
            
            return {
                "status": "success",
                "conversion_id": conversion_id,
                "conversion": conversion
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_conversion(
        self,
        conversion_id: str
    ) -> dict:
        """Get conversion details."""
        return self.conversions.get(conversion_id, {
            "error": f"Unknown conversion: {conversion_id}"
        })

# Usage
def convert_data():
    """Demo data conversion."""
    # Create converter
    converter = DataConverter(
        save_dir="data_conversions"
    )
    
    # Convert CSV to JSON
    result = converter.convert_file(
        source="data/users.csv",
        target="data/users.json",
        schema={
            "id": int,
            "name": str,
            "email": str
        }
    )
    print("\nConversion:", result)
    
    return result
```

## Advanced Adapters

### Custom Adapters
```python
from lionagi.protocols.adapters import Adapter
from typing import Any, TypeVar

T = TypeVar("T")

class YAMLAdapter(Adapter):
    """Custom YAML adapter."""
    obj_key = ".yaml"
    
    @classmethod
    def from_obj(
        cls,
        subj_cls: type[T],
        obj: Any,
        /,
        *,
        many: bool = False,
        **kwargs
    ) -> dict | list[dict]:
        """Convert from YAML."""
        import yaml
        data = yaml.safe_load(obj)
        if many:
            return data if isinstance(data, list) else [data]
        return data
    
    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        *,
        many: bool = False,
        **kwargs
    ) -> str:
        """Convert to YAML."""
        import yaml
        if many:
            data = [i.to_dict() for i in subj]
        else:
            data = subj.to_dict()
        return yaml.dump(data, **kwargs)

class XMLAdapter(Adapter):
    """Custom XML adapter."""
    obj_key = ".xml"
    
    @classmethod
    def from_obj(
        cls,
        subj_cls: type[T],
        obj: Any,
        /,
        *,
        many: bool = False,
        **kwargs
    ) -> dict | list[dict]:
        """Convert from XML."""
        import xmltodict
        data = xmltodict.parse(obj)
        if many:
            return data if isinstance(data, list) else [data]
        return data
    
    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        *,
        many: bool = False,
        **kwargs
    ) -> str:
        """Convert to XML."""
        import xmltodict
        if many:
            data = [i.to_dict() for i in subj]
        else:
            data = subj.to_dict()
        return xmltodict.unparse(data, **kwargs)
```

## Real-World Example

### Data Integration Pipeline
```python
from lionagi import Branch, Model, types
from lionagi.protocols.adapters import Adapter
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import json

class DataSource(Form):
    """Data source configuration."""
    name: str = Field(
        description="Source name"
    )
    type: str = Field(
        description="Source type",
        pattern="^(file|api|database)$"
    )
    format: str = Field(
        description="Data format"
    )
    location: str = Field(
        description="Data location"
    )
    schema: Dict[str, Any] = Field(
        description="Data schema"
    )

class DataTarget(Form):
    """Data target configuration."""
    name: str = Field(
        description="Target name"
    )
    type: str = Field(
        description="Target type",
        pattern="^(file|api|database)$"
    )
    format: str = Field(
        description="Data format"
    )
    location: str = Field(
        description="Data location"
    )
    schema: Dict[str, Any] = Field(
        description="Data schema"
    )

class IntegrationPipeline:
    """Complete data integration pipeline."""
    def __init__(
        self,
        name: str = "Pipeline",
        save_dir: str = "integrations"
    ):
        # Setup storage
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Create converter
        self.converter = DataConverter(
            save_dir=f"{save_dir}/conversions"
        )
        
        # Track integrations
        self.sources: Dict[str, dict] = {}
        self.targets: Dict[str, dict] = {}
        self.pipelines: Dict[str, dict] = {}
    
    async def add_source(
        self,
        config: dict
    ) -> dict:
        """Add data source."""
        try:
            # Validate config
            source = DataSource(**config)
            
            # Record source
            source_id = f"source_{len(self.sources)}"
            self.sources[source_id] = source.model_dump()
            
            return {
                "status": "success",
                "source_id": source_id
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def add_target(
        self,
        config: dict
    ) -> dict:
        """Add data target."""
        try:
            # Validate config
            target = DataTarget(**config)
            
            # Record target
            target_id = f"target_{len(self.targets)}"
            self.targets[target_id] = target.model_dump()
            
            return {
                "status": "success",
                "target_id": target_id
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def create_pipeline(
        self,
        source_id: str,
        target_id: str
    ) -> dict:
        """Create integration pipeline."""
        if source_id not in self.sources:
            return {
                "status": "error",
                "error": f"Unknown source: {source_id}"
            }
        
        if target_id not in self.targets:
            return {
                "status": "error",
                "error": f"Unknown target: {target_id}"
            }
        
        try:
            # Get configs
            source = self.sources[source_id]
            target = self.targets[target_id]
            
            # Create pipeline
            pipeline_id = f"pipeline_{len(self.pipelines)}"
            pipeline = {
                "id": pipeline_id,
                "source": source,
                "target": target,
                "status": "created",
                "timestamp": datetime.now().isoformat()
            }
            
            # Record pipeline
            self.pipelines[pipeline_id] = pipeline
            
            return {
                "status": "success",
                "pipeline_id": pipeline_id,
                "pipeline": pipeline
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_pipeline(
        self,
        pipeline_id: str
    ) -> dict:
        """Run integration pipeline."""
        if pipeline_id not in self.pipelines:
            return {
                "status": "error",
                "error": f"Unknown pipeline: {pipeline_id}"
            }
        
        try:
            pipeline = self.pipelines[pipeline_id]
            source = pipeline["source"]
            target = pipeline["target"]
            
            # Convert data
            result = self.converter.convert_file(
                source=source["location"],
                target=target["location"],
                schema=source["schema"]
            )
            
            if result["status"] != "success":
                return result
            
            # Update pipeline
            pipeline["conversion"] = result["conversion"]
            pipeline["status"] = "completed"
            pipeline["completed"] = datetime.now().isoformat()
            
            return {
                "status": "success",
                "pipeline_id": pipeline_id,
                "result": result
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_pipeline(
        self,
        pipeline_id: str
    ) -> dict:
        """Get pipeline details."""
        return self.pipelines.get(pipeline_id, {
            "error": f"Unknown pipeline: {pipeline_id}"
        })

# Usage
async def run_integration():
    """Demo data integration."""
    # Create pipeline
    pipeline = IntegrationPipeline(
        name="DataIntegration",
        save_dir="integration_data"
    )
    
    # Add source
    source = {
        "name": "UserData",
        "type": "file",
        "format": "csv",
        "location": "data/users.csv",
        "schema": {
            "id": int,
            "name": str,
            "email": str
        }
    }
    
    source_result = await pipeline.add_source(source)
    print("\nSource:", source_result)
    
    # Add target
    target = {
        "name": "UserAPI",
        "type": "file",
        "format": "json",
        "location": "data/users.json",
        "schema": {
            "id": int,
            "name": str,
            "email": str
        }
    }
    
    target_result = await pipeline.add_target(target)
    print("\nTarget:", target_result)
    
    # Create pipeline
    if (source_result["status"] == "success" and
        target_result["status"] == "success"):
        # Create pipeline
        create_result = await pipeline.create_pipeline(
            source_result["source_id"],
            target_result["target_id"]
        )
        print("\nPipeline:", create_result)
        
        # Run pipeline
        if create_result["status"] == "success":
            run_result = await pipeline.run_pipeline(
                create_result["pipeline_id"]
            )
            print("\nResult:", run_result)

# Run integration
asyncio.run(run_integration())
```

## Best Practices

1. **Adapter Design**
   - Keep adapters focused
   - Handle validation
   - Support schemas
   - Handle errors

2. **Pipeline Design**
   - Validate configs
   - Track progress
   - Handle failures
   - Monitor results

3. **Integration Design**
   - Check compatibility
   - Transform data
   - Validate results
   - Log operations

## Quick Reference
```python
from lionagi.protocols.adapters import (
    JsonAdapter,
    CSVFileAdapter
)

# Convert JSON
data = JsonAdapter.from_obj(
    dict,
    json_string,
    many=True
)

# Save CSV
CSVFileAdapter.to_obj(
    data,
    fp="output.csv",
    many=True
)
```

## Next Steps

You've learned:
- How to use adapters
- How to convert formats
- How to validate data
- How to build pipelines

In [Chapter 10](ch10_e2e_project.md), we'll build a complete end-to-end project.

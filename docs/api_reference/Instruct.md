# Instruction System API Reference

## Overview

The Instruction system helps define and manage AI tasks by providing:
- Clear task definitions with guidance and context
- Task sequencing through graph relationships
- Collection management for grouped tasks
- Decision tracking with confidence scoring

## Components

### Instruct

Core class for defining what an AI should do and how it should do it.

```python
class Instruct(HashableModel):
    """Task instruction with execution details."""
    
    instruction: JsonValue | None     # What to do
    guidance: JsonValue | None        # How to do it
    context: JsonValue | None         # Relevant information
    reason: bool = False             # Whether to explain decisions
    actions: bool = False            # Whether to execute actions

# Define data analysis task
analysis = Instruct(
    instruction={
        "task": "Analyze user engagement",
        "metrics": ["daily_active", "session_length"],
        "output": "summary report"
    },
    guidance={
        "method": "cohort analysis",
        "focus": "retention patterns",
        "depth": "last 6 months"
    },
    context={
        "data_source": "user_events.db",
        "baseline_metrics": {"daily_active": 10000},
        "critical_segments": ["new_users", "power_users"]
    }
)
```

### InstructNode

Enables organizing tasks into workflows by connecting them in a graph.

```python
class InstructNode(Node):
    """Graph node for connected instructions."""
    
    instruct: Instruct | None
    
    def add_edge(self, target: Node, label: str) -> None:
        """Connect to another instruction."""

# Create data pipeline workflow
extract = InstructNode(
    instruct=Instruct(
        instruction={
            "task": "Extract user data",
            "source": "production_db",
            "tables": ["users", "events"]
        }
    )
)

transform = InstructNode(
    instruct=Instruct(
        instruction={
            "task": "Clean and transform data",
            "operations": ["dedup", "normalize"]
        }
    )
)

analyze = InstructNode(
    instruct=Instruct(
        instruction={
            "task": "Generate insights",
            "metrics": ["engagement", "retention"]
        }
    )
)

# Create workflow
extract.add_edge(transform, "next")
transform.add_edge(analyze, "next")
```

### InstructCollection

Manages groups of related instructions, useful for batch processing or complex tasks.

```python
class InstructCollection(BaseModel):
    """Manages groups of related instructions."""
    
    @property
    def instruct_models(self) -> list[Instruct]:
        """Get all instructions in collection."""
        
    def to_instruct_nodes(self) -> list[InstructNode]:
        """Convert to connected graph nodes."""

# Create collection for multi-market analysis
params = InstructCollection.create_model_params(num_instructs=3)
MarketAnalysis = params.create_new_model()

analysis = MarketAnalysis()
analysis.instruct_0 = Instruct(
    instruction={
        "task": "Market size analysis",
        "regions": ["NA", "EU", "APAC"]
    }
)
analysis.instruct_1 = Instruct(
    instruction={
        "task": "Competitor analysis",
        "focus": ["market share", "pricing"]
    }
)
analysis.instruct_2 = Instruct(
    instruction={
        "task": "Growth opportunities",
        "output": "strategic recommendations"
    }
)
```

### Reason

Tracks decision rationale and confidence levels, useful for auditing and improving AI decisions.

```python
class Reason(BaseModel):
    """Decision reasoning tracker."""
    
    title: str | None = None          # Decision summary
    content: str | None = None        # Detailed explanation
    confidence_score: float | None    # How confident (0.0-1.0)

# Track strategic decision
reason = Reason(
    title="Market Entry Strategy",
    content="""
    Recommended entering APAC market first due to:
    1. Larger addressable market (2.1B users)
    2. Lower competition (3 major players vs 8 in EU)
    3. Higher growth rate (27% YoY vs 12% in NA)
    """,
    confidence_score=0.87  # High confidence but not certain
)
```

## Common Use Cases

### Complex Analysis Task

```python
# Define comprehensive market analysis
market_analysis = Instruct(
    instruction={
        "task": "Analyze market opportunity",
        "regions": ["NA", "EU", "APAC"],
        "aspects": ["size", "competition", "regulation"],
        "deliverable": "go-to-market strategy"
    },
    guidance={
        "framework": "Porter's Five Forces",
        "data_sources": ["market_reports", "competitor_data"],
        "output_format": "executive summary"
    },
    context={
        "company_stage": "series B",
        "current_markets": ["NA"],
        "budget_constraint": "5M USD",
        "time_horizon": "18 months"
    },
    reason=True  # Include decision rationale
)
```

### Multi-Step Data Processing

```python
# Create data quality pipeline
def create_data_pipeline():
    steps = [
        ("validate", {
            "task": "Validate data quality",
            "checks": ["completeness", "accuracy"]
        }),
        ("clean", {
            "task": "Clean data issues",
            "operations": ["dedup", "standardize"]
        }),
        ("enrich", {
            "task": "Enrich data",
            "sources": ["external_api", "ml_models"]
        })
    ]
    
    # Create nodes
    nodes = []
    for name, config in steps:
        node = InstructNode(
            instruct=Instruct(
                instruction=config,
                context={"pipeline_id": "data_quality_v1"}
            )
        )
        nodes.append(node)
    
    # Connect workflow
    for i in range(len(nodes)-1):
        nodes[i].add_edge(nodes[i+1], "next")
    
    return nodes

pipeline = create_data_pipeline()
```

### Decision Recording

```python
# Track model selection decision
model_selection = Instruct(
    instruction={
        "task": "Select ML model",
        "criteria": ["accuracy", "latency", "cost"]
    },
    context={
        "data_size": "10TB",
        "latency_req": "<100ms",
        "budget": "10K/month"
    },
    reason=True
)

decision = Reason(
    title="Selected DistilBERT Model",
    content="""
    Selected DistilBERT over BERT based on:
    1. 95% of BERT accuracy
    2. 40% faster inference
    3. 60% lower compute cost
    Trade-off: Slightly lower accuracy (2%) for major performance gains.
    """,
    confidence_score=0.92
)
```

# Dataset Validation Framework

## Overview
This document outlines the validation framework for ensuring quality and consistency across all dataset examples. It provides concrete validation rules, testing approaches, and quality assurance procedures.

## Core Validation Components

### 1. Schema Validation
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional

class MessageContent(BaseModel):
    role: Literal["system", "user", "assistant", "action"]
    content: str
    reasoning: Optional[str] = None
    tool_call: Optional[Dict] = None

class DatasetExample(BaseModel):
    type: Literal["basic_chat", "tool_usage", "react_basic"]
    metadata: Dict
    description: str
    messages: List[MessageContent]
    expected_behavior: Dict

    class Config:
        extra = "forbid"  # Prevent additional fields
```

### 2. Pattern-Specific Validators

```python
class ValidationResult:
    def __init__(self):
        self.passed = True
        self.errors = []
        self.warnings = []

class PatternValidator:
    @staticmethod
    def validate_basic_chat(example: Dict) -> ValidationResult:
        result = ValidationResult()
        
        # Check message sequence
        roles = [m["role"] for m in example["messages"]]
        if "user" not in roles:
            result.passed = False
            result.errors.append("Missing user message")
        if "assistant" not in roles:
            result.passed = False
            result.errors.append("Missing assistant response")
            
        return result

    @staticmethod
    def validate_tool_usage(example: Dict) -> ValidationResult:
        result = ValidationResult()
        
        # Check tool calls
        action_messages = [m for m in example["messages"] if m["role"] == "action"]
        if not action_messages:
            result.passed = False
            result.errors.append("No tool calls found")
            
        return result

    @staticmethod
    def validate_react(example: Dict) -> ValidationResult:
        result = ValidationResult()
        
        # Check reasoning
        reasoning_messages = [
            m for m in example["messages"] 
            if m["role"] == "assistant" and "reasoning" in m
        ]
        if not reasoning_messages:
            result.passed = False
            result.errors.append("No reasoning steps found")
            
        return result
```

## Validation Pipeline

### 1. Pre-processing Checks
```python
def preprocess_example(example: Dict) -> Dict:
    """Prepare example for validation"""
    # Normalize whitespace
    for message in example["messages"]:
        message["content"] = message["content"].strip()
        if "reasoning" in message:
            message["reasoning"] = message["reasoning"].strip()
    
    return example
```

### 2. Core Validation Steps
```python
def validate_example(example: Dict) -> ValidationResult:
    """Complete validation pipeline for a single example"""
    result = ValidationResult()
    
    # 1. Schema validation
    try:
        DatasetExample(**example)
    except Exception as e:
        result.passed = False
        result.errors.append(f"Schema validation failed: {str(e)}")
        return result
    
    # 2. Pattern-specific validation
    pattern_result = {
        "basic_chat": PatternValidator.validate_basic_chat,
        "tool_usage": PatternValidator.validate_tool_usage,
        "react_basic": PatternValidator.validate_react
    }[example["type"]](example)
    
    result.passed &= pattern_result.passed
    result.errors.extend(pattern_result.errors)
    result.warnings.extend(pattern_result.warnings)
    
    return result
```

### 3. Quality Checks
```python
def quality_check_example(example: Dict) -> List[str]:
    """Additional quality checks beyond basic validation"""
    suggestions = []
    
    # Check description quality
    if len(example["description"]) < 20:
        suggestions.append("Description could be more detailed")
    
    # Check message content quality
    for msg in example["messages"]:
        if len(msg["content"]) < 10:
            suggestions.append(f"Short content in {msg['role']} message")
        
        if msg["role"] == "assistant":
            if not any(char in msg["content"] for char in ".,;:"):
                suggestions.append("Assistant response lacks proper punctuation")
    
    return suggestions
```

## Usage Examples

### 1. Validating a Single Example
```python
def process_example(example: Dict) -> bool:
    """Process and validate a single example"""
    # Preprocess
    example = preprocess_example(example)
    
    # Validate
    result = validate_example(example)
    if not result.passed:
        print("Validation failed:")
        for error in result.errors:
            print(f"- {error}")
        return False
    
    # Quality check
    suggestions = quality_check_example(example)
    if suggestions:
        print("Quality suggestions:")
        for suggestion in suggestions:
            print(f"- {suggestion}")
    
    return True
```

### 2. Batch Validation
```python
def validate_dataset(examples: List[Dict]) -> Dict:
    """Validate entire dataset"""
    results = {
        "total": len(examples),
        "passed": 0,
        "failed": 0,
        "warnings": 0,
        "errors": []
    }
    
    for i, example in enumerate(examples):
        result = validate_example(example)
        if result.passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["errors"].append({
                "example_index": i,
                "errors": result.errors
            })
        
        if result.warnings:
            results["warnings"] += 1
    
    return results
```

## Implementation Guidelines

### 1. Running Validation
```python
# Single example
example = {
    "type": "basic_chat",
    "metadata": {...},
    "description": "Test example",
    "messages": [...]
}
process_example(example)

# Full dataset
dataset = load_dataset("path/to/dataset.json")
results = validate_dataset(dataset)
```

### 2. Handling Results
```python
def handle_validation_results(results: Dict):
    """Process validation results"""
    print(f"Validation Summary:")
    print(f"Total examples: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"With warnings: {results['warnings']}")
    
    if results['errors']:
        print("\nErrors found:")
        for error in results['errors']:
            print(f"\nExample {error['example_index']}:")
            for err in error['errors']:
                print(f"- {err}")
```

## Quality Metrics

### 1. Coverage Metrics
- Percentage of examples passing validation
- Distribution of pattern types
- Tool usage coverage
- Error scenario coverage

### 2. Content Quality Metrics
- Description completeness
- Reasoning step clarity
- Tool usage appropriateness
- Response comprehensiveness

## Maintenance

### 1. Regular Checks
- Run validation on all new examples
- Periodic full dataset validation
- Quality metric tracking
- Pattern distribution monitoring

### 2. Update Process
- Document validation changes
- Version control for validators
- Backward compatibility checks
- Migration scripts if needed

## Next Steps

1. Implementation Priority
   - Schema validation
   - Basic pattern validators
   - Quality checks
   - Reporting system

2. Integration Points
   - CI/CD pipeline
   - Dataset generation tools
   - Quality monitoring
   - Documentation updates

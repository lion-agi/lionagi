# Basic Chat Pattern Documentation

## Overview
This document outlines the structure and implementation of basic chat interactions in the LionAGI dataset. These examples capture direct question-answer flows without tool usage.

## Pattern Structure

```python
{
    "type": "basic_chat",
    "metadata": {
        "pattern_version": "1.0",
        "complexity_level": "basic",
        "interaction_type": "direct"
    },
    "description": str,  # Clear description of the interaction
    "messages": [
        {
            "role": str,      # system/user/assistant
            "content": str    # The actual message content
        }
    ],
    "expected_behavior": {
        "reasoning_style": str,    # e.g., "step-by-step", "direct"
        "response_format": str,    # e.g., "natural", "structured"
        "key_elements": List[str]  # Required elements in response
    }
}
```

## Example Scenarios

### 1. Simple Question-Answer
```python
{
    "type": "basic_chat",
    "description": "Direct question about LionAGI's purpose",
    "messages": [
        {
            "role": "system",
            "content": "You are an AI assistant focused on explaining LionAGI's capabilities clearly and accurately."
        },
        {
            "role": "user",
            "content": "What is the main purpose of LionAGI?"
        },
        {
            "role": "assistant",
            "content": "LionAGI is an intelligence operating system designed for orchestrated automated intelligence. Its main purposes are:\n1. Reliable intelligence processing\n2. Explainable operations\n3. Structured communication\n4. Coordinated tool usage"
        }
    ],
    "expected_behavior": {
        "reasoning_style": "structured",
        "response_format": "natural",
        "key_elements": ["definition", "key_features", "practical_use"]
    }
}
```

### 2. Multi-turn Conversation
```python
{
    "type": "basic_chat",
    "description": "Follow-up questions about specific features",
    "messages": [
        {
            "role": "system",
            "content": "You are an AI assistant focused on explaining LionAGI's capabilities clearly and accurately."
        },
        {
            "role": "user",
            "content": "How does LionAGI handle message processing?"
        },
        {
            "role": "assistant",
            "content": "LionAGI processes messages through a structured protocol system that includes:\n1. Role-based message handling\n2. State management\n3. Context preservation"
        },
        {
            "role": "user",
            "content": "Can you explain more about role-based handling?"
        },
        {
            "role": "assistant",
            "content": "Role-based message handling in LionAGI uses predefined roles like SYSTEM, USER, ASSISTANT, and ACTION. Each role has specific responsibilities:\n- SYSTEM: Provides context and guidelines\n- USER: Represents input queries\n- ASSISTANT: Handles responses and reasoning\n- ACTION: Manages tool interactions"
        }
    ],
    "expected_behavior": {
        "reasoning_style": "explanatory",
        "response_format": "natural",
        "key_elements": ["concept_explanation", "examples", "follow_up_handling"]
    }
}
```

## Validation Criteria

### Required Elements
1. System message (optional but recommended)
2. At least one user message
3. Corresponding assistant response
4. Clear progression of conversation

### Content Guidelines
1. Assistant responses should be:
   - Clear and focused
   - Properly formatted
   - Contextually appropriate
   - Factually accurate regarding LionAGI

2. System messages should:
   - Set clear context
   - Define response expectations
   - Establish any constraints

### Quality Checks
```python
def validate_basic_chat(example):
    """
    Validation function for basic chat examples
    """
    # Required fields
    assert "type" in example and example["type"] == "basic_chat"
    assert "description" in example
    assert "messages" in example
    
    # Message sequence validation
    messages = example["messages"]
    assert len(messages) >= 2  # At least user + assistant
    
    # Role sequence validation
    roles = [m["role"] for m in messages]
    assert "user" in roles
    assert "assistant" in roles
    
    # Content validation
    for message in messages:
        assert "content" in message
        assert len(message["content"].strip()) > 0
```

## Usage Notes

### When to Use
- Direct information queries
- Concept explanations
- Feature clarifications
- Multi-turn discussions without tool needs

### When Not to Use
- Tasks requiring tool interaction
- Complex problem-solving
- Data manipulation needs
- External resource requirements

## Extension Points

### Future Enhancements
1. Add support for:
   - Rich text formatting
   - Code snippets
   - Structured data responses
   - Message threading

2. Integration with:
   - Knowledge graph
   - Context management
   - State tracking

## Test Cases

### Basic Validation
```python
test_cases = [
    {
        "input": {
            "type": "basic_chat",
            "messages": [
                {"role": "user", "content": "What is LionAGI?"},
                {"role": "assistant", "content": "LionAGI is..."}
            ]
        },
        "expected": True
    },
    {
        "input": {
            "type": "basic_chat",
            "messages": [
                {"role": "user", "content": ""}  # Invalid: empty content
            ]
        },
        "expected": False
    }
]
```

### Edge Cases
1. Empty messages list
2. Missing roles
3. Invalid role types
4. Malformed content
5. Missing required fields

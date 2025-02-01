# Tool Usage Pattern Documentation

## Overview
This document outlines the structure and implementation of basic tool usage interactions in the LionAGI dataset. These examples capture how LionAGI handles tool selection, execution, and result processing.

## Pattern Structure

```python
{
    "type": "tool_usage",
    "metadata": {
        "pattern_version": "1.0",
        "complexity_level": "basic",
        "interaction_type": "tool_based"
    },
    "description": str,  # Clear description of the tool interaction
    "messages": [
        {
            "role": str,      # system/user/assistant/action
            "content": str,   # Message or tool call content
            "tool_call": {    # Only present in action messages
                "name": str,
                "arguments": dict
            }
        }
    ],
    "expected_behavior": {
        "tool_selection": str,     # Why this tool was chosen
        "argument_handling": str,  # How arguments should be processed
        "result_processing": str   # How tool results should be interpreted
    }
}
```

## Example Scenarios

### 1. File Reading Operation
```python
{
    "type": "tool_usage",
    "description": "Reading and analyzing a configuration file",
    "messages": [
        {
            "role": "system",
            "content": "You are an AI assistant capable of reading and analyzing files."
        },
        {
            "role": "user",
            "content": "What are the contents of config.json?"
        },
        {
            "role": "assistant",
            "content": "I'll read the config.json file to examine its contents."
        },
        {
            "role": "action",
            "content": "Reading file: config.json",
            "tool_call": {
                "name": "read_file",
                "arguments": {
                    "path": "config.json"
                }
            }
        },
        {
            "role": "assistant",
            "content": "The config.json file contains the following settings:\n1. API endpoint: https://api.example.com\n2. Debug mode: enabled\n3. Max retries: 3"
        }
    ],
    "expected_behavior": {
        "tool_selection": "read_file tool is appropriate for accessing file contents",
        "argument_handling": "path parameter should be validated",
        "result_processing": "JSON content should be parsed and presented clearly"
    }
}
```

### 2. Browser Interaction
```python
{
    "type": "tool_usage",
    "description": "Interacting with a webpage",
    "messages": [
        {
            "role": "system",
            "content": "You are an AI assistant capable of browser interactions."
        },
        {
            "role": "user",
            "content": "Open the documentation page and click the 'Get Started' button"
        },
        {
            "role": "assistant",
            "content": "I'll use the browser tool to navigate to the page and click the button."
        },
        {
            "role": "action",
            "content": "Opening browser at documentation page",
            "tool_call": {
                "name": "browser_action",
                "arguments": {
                    "action": "launch",
                    "url": "http://localhost:3000/docs"
                }
            }
        },
        {
            "role": "action",
            "content": "Clicking 'Get Started' button",
            "tool_call": {
                "name": "browser_action",
                "arguments": {
                    "action": "click",
                    "coordinate": "150,200"
                }
            }
        },
        {
            "role": "assistant",
            "content": "I've opened the documentation page and clicked the 'Get Started' button. The page has now navigated to the getting started guide."
        }
    ],
    "expected_behavior": {
        "tool_selection": "browser_action tool for web interaction",
        "argument_handling": "proper action sequencing and coordinate validation",
        "result_processing": "confirmation of successful actions"
    }
}
```

## Validation Criteria

### Required Elements
1. Clear tool selection reasoning
2. Proper argument formatting
3. Result interpretation
4. Error handling consideration

### Content Guidelines
1. Tool calls should:
   - Use correct tool names
   - Provide valid arguments
   - Include error handling
   - Process results appropriately

2. Assistant messages should:
   - Explain tool selection
   - Interpret results clearly
   - Handle errors gracefully

### Quality Checks
```python
def validate_tool_usage(example):
    """
    Validation function for tool usage examples
    """
    # Required fields
    assert "type" in example and example["type"] == "tool_usage"
    assert "description" in example
    assert "messages" in example
    
    # Message sequence validation
    messages = example["messages"]
    has_tool_call = False
    for msg in messages:
        if msg["role"] == "action":
            has_tool_call = True
            assert "tool_call" in msg
            assert "name" in msg["tool_call"]
            assert "arguments" in msg["tool_call"]
    
    assert has_tool_call, "Example must include at least one tool call"
    
    # Tool call validation
    tool_calls = [m for m in messages if m["role"] == "action"]
    for call in tool_calls:
        assert isinstance(call["tool_call"]["arguments"], dict)
```

## Usage Notes

### When to Use
- File operations
- Browser interactions
- Code analysis
- Data queries

### When Not to Use
- Simple information requests
- Complex multi-tool scenarios
- Purely conversational interactions

## Extension Points

### Future Enhancements
1. Add support for:
   - Tool chaining
   - Result caching
   - Argument validation
   - Error recovery

2. Integration with:
   - Tool schema validation
   - Result type checking
   - Performance monitoring

## Test Cases

### Basic Validation
```python
test_cases = [
    {
        "input": {
            "type": "tool_usage",
            "messages": [
                {"role": "user", "content": "Read file.txt"},
                {"role": "action", "tool_call": {
                    "name": "read_file",
                    "arguments": {"path": "file.txt"}
                }}
            ]
        },
        "expected": True
    },
    {
        "input": {
            "type": "tool_usage",
            "messages": [
                {"role": "action", "tool_call": {
                    "name": "invalid_tool"  # Invalid: unknown tool
                }}
            ]
        },
        "expected": False
    }
]
```

### Edge Cases
1. Invalid tool names
2. Missing arguments
3. Invalid argument types
4. Failed tool execution
5. Timeout scenarios

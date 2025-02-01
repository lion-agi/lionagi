# ReAct Pattern Documentation

## Overview
This document outlines the structure and implementation of ReAct (Reasoning + Action) patterns in the LionAGI dataset. These examples demonstrate how LionAGI combines step-by-step reasoning with tool usage to solve problems.

## Pattern Structure

```python
{
    "type": "react_basic",
    "metadata": {
        "pattern_version": "1.0",
        "complexity_level": "intermediate",
        "interaction_type": "reasoning_with_tools"
    },
    "description": str,  # Clear description of the problem-solving scenario
    "messages": [
        {
            "role": str,      # system/user/assistant/action
            "content": str,   # Message, reasoning, or tool call content
            "reasoning": str, # Present in assistant messages with analysis
            "tool_call": {    # Present in action messages
                "name": str,
                "arguments": dict
            }
        }
    ],
    "expected_behavior": {
        "reasoning_steps": List[str],  # Expected analysis steps
        "tool_usage": List[str],      # Expected tool interactions
        "success_criteria": List[str]  # What defines a good solution
    }
}
```

## Example Scenarios

### 1. Code Analysis with ReAct
```python
{
    "type": "react_basic",
    "description": "Analyze Python files in a directory for TODO comments",
    "messages": [
        {
            "role": "system",
            "content": "You are an AI assistant that combines reasoning with actions to solve problems effectively."
        },
        {
            "role": "user",
            "content": "Find all TODO comments in the src directory and summarize what needs to be done."
        },
        {
            "role": "assistant",
            "content": "I'll analyze this step by step.",
            "reasoning": """
1. First, I need to search through all Python files for TODO comments
2. Then I'll collect and categorize the findings
3. Finally, I'll provide a structured summary
            """
        },
        {
            "role": "action",
            "content": "Searching for TODO comments",
            "tool_call": {
                "name": "search_files",
                "arguments": {
                    "path": "src",
                    "regex": "# TODO:",
                    "file_pattern": "*.py"
                }
            }
        },
        {
            "role": "assistant",
            "content": "I found several TODO comments. Let me analyze them.",
            "reasoning": """
1. The TODOs appear to fall into categories:
   - Feature implementations
   - Bug fixes
   - Performance improvements
2. Let me organize them by priority
            """
        },
        {
            "role": "assistant",
            "content": """Here's a summary of pending tasks:

Priority 1 (Bug Fixes):
- Fix user authentication timeout issue
- Handle edge case in data processing

Priority 2 (Features):
- Implement caching mechanism
- Add support for new file formats

Priority 3 (Improvements):
- Optimize database queries
- Refactor error handling logic"""
        }
    ],
    "expected_behavior": {
        "reasoning_steps": [
            "Plan search approach",
            "Execute search",
            "Analyze findings",
            "Categorize results",
            "Present structured summary"
        ],
        "tool_usage": [
            "Use search_files with appropriate regex",
            "Process search results effectively"
        ],
        "success_criteria": [
            "All Python files searched",
            "TODOs properly categorized",
            "Clear priority structure",
            "Actionable summary"
        ]
    }
}
```

### 2. Multi-Step Problem Solving
```python
{
    "type": "react_basic",
    "description": "Analyze a configuration file and validate its settings",
    "messages": [
        {
            "role": "system",
            "content": "You are an AI assistant that combines reasoning with actions to solve problems effectively."
        },
        {
            "role": "user",
            "content": "Check if the database settings in config.json are properly configured for production use."
        },
        {
            "role": "assistant",
            "content": "I'll analyze this systematically.",
            "reasoning": """
1. First, I need to read the config file
2. Then analyze the database settings
3. Compare against production requirements
4. Validate security settings
            """
        },
        {
            "role": "action",
            "content": "Reading configuration file",
            "tool_call": {
                "name": "read_file",
                "arguments": {
                    "path": "config.json"
                }
            }
        },
        {
            "role": "assistant",
            "content": "Let me analyze the database configuration.",
            "reasoning": """
1. Checking required fields:
   - Connection string ✓
   - Max connections ✓
   - Timeout settings ✓
2. Security analysis:
   - SSL enabled ✓
   - Authentication required ✓
3. Production readiness:
   - Need to verify connection pool settings
            """
        },
        {
            "role": "assistant",
            "content": """Database configuration analysis results:

✅ Core Settings:
- All required fields present
- Connection string properly formatted
- Timeout values appropriate

⚠️ Security Settings:
- SSL is enabled
- Authentication is required
- Recommend enabling connection encryption

🔧 Production Recommendations:
1. Increase connection pool size
2. Add retry mechanism
3. Enable query logging"""
        }
    ],
    "expected_behavior": {
        "reasoning_steps": [
            "Plan analysis approach",
            "Read configuration",
            "Analyze settings",
            "Check security",
            "Provide recommendations"
        ],
        "tool_usage": [
            "Read file contents",
            "Parse JSON structure",
            "Validate settings"
        ],
        "success_criteria": [
            "All settings checked",
            "Security validated",
            "Clear recommendations",
            "Actionable feedback"
        ]
    }
}
```

## Validation Criteria

### Required Elements
1. Clear reasoning steps
2. Appropriate tool usage
3. Structured analysis
4. Actionable conclusions

### Content Guidelines
1. Reasoning should:
   - Be clear and logical
   - Show step-by-step thinking
   - Justify tool usage
   - Lead to concrete actions

2. Tool usage should:
   - Follow from reasoning
   - Be appropriate for the task
   - Handle errors gracefully
   - Produce useful results

### Quality Checks
```python
def validate_react_pattern(example):
    """
    Validation function for ReAct pattern examples
    """
    # Required fields
    assert "type" in example and example["type"] == "react_basic"
    assert "description" in example
    assert "messages" in example
    
    # Message sequence validation
    messages = example["messages"]
    has_reasoning = False
    has_tool_call = False
    
    for msg in messages:
        if msg["role"] == "assistant" and "reasoning" in msg:
            has_reasoning = True
        if msg["role"] == "action":
            has_tool_call = True
            assert "tool_call" in msg
    
    assert has_reasoning, "Example must include reasoning steps"
    assert has_tool_call, "Example must include tool usage"
    
    # Reasoning quality checks
    reasoning_messages = [m for m in messages if m["role"] == "assistant" and "reasoning" in m]
    for msg in reasoning_messages:
        assert len(msg["reasoning"].strip().split("\n")) >= 2, "Reasoning should have multiple steps"
```

## Usage Notes

### When to Use
- Complex problem solving
- Multi-step analysis
- Tool-assisted reasoning
- Structured investigations

### When Not to Use
- Simple queries
- Single tool operations
- Direct information requests
- Basic chat interactions

## Extension Points

### Future Enhancements
1. Add support for:
   - Multiple reasoning strategies
   - Advanced tool combinations
   - Result verification
   - Alternative approaches

2. Integration with:
   - Learning mechanisms
   - Performance optimization
   - Error recovery strategies

## Test Cases

### Basic Validation
```python
test_cases = [
    {
        "input": {
            "type": "react_basic",
            "messages": [
                {
                    "role": "assistant",
                    "reasoning": "1. First step\n2. Second step"
                },
                {
                    "role": "action",
                    "tool_call": {"name": "read_file", "arguments": {}}
                }
            ]
        },
        "expected": True
    },
    {
        "input": {
            "type": "react_basic",
            "messages": [
                {
                    "role": "assistant",
                    "reasoning": "Single step"  # Invalid: insufficient reasoning
                }
            ]
        },
        "expected": False
    }
]
```

### Edge Cases
1. Missing reasoning steps
2. Incomplete tool usage
3. Circular reasoning
4. Failed tool calls
5. Inconclusive analysis

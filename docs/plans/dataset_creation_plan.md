# LionAGI Dataset Creation Plan

## Overview
Create a comprehensive dataset that captures LionAGI's advanced capabilities, focusing on multi-turn reasoning, tool usage, multi-branch conversations, and ReAct patterns. This dataset will serve as a foundation for demonstrating and training LionAGI's sophisticated features.

## Core Components

### 1. Advanced LionAGI Features
- Multi-turn conversations (branch.communicate, branch.chat, branch.operate)
- Action system (ActionRequest, ActionResponse)
- ReAct reasoning with expansions
- Multi-branch orchestration via Session
- Mail exchange for cross-branch communication

### 2. Message Types
- System messages
- Instructions
- Assistant responses
- Action requests/responses
- Mail items for cross-branch communication

### 3. Branch Operations
- communicate: Transform + predict + transform
- operate: Transform + predict + transform + act + transform
- ReAct: Transform + operate + chain_loop[operate] + communicate
- act: Direct tool interactions

## Dataset Structure

```python
{
    "scenario_name": str,          # Descriptive name of the scenario
    "description": str,            # Detailed explanation of features demonstrated
    "branches": [
        {
            "branch_name": str,    # Identifier for this branch
            "messages": [
                {
                    "role": str,   # system/user/assistant/action
                    "content": str, # Message content
                    "reasoning": Optional[str],  # For ReAct expansions
                    "tool_call": Optional[dict]  # For action messages
                }
            ]
        }
    ],
    "mail_exchanges": [           # Cross-branch communication
        {
            "source_branch": str,
            "target_branch": str,
            "mail_items": [
                {
                    "sender": str,
                    "recipient": str,
                    "package": dict
                }
            ]
        }
    ],
    "tools_used": [              # Tool interaction summary
        {
            "name": str,
            "calls": [
                {
                    "arguments": dict,
                    "result": Any
                }
            ]
        }
    ],
    "final_outcome": str         # Scenario resolution
}
```

## Implementation Phases

### Phase 1: Core Single-Branch Examples (Week 1-2)
1. Basic Communication
   - Simple chat interactions
   - Instruction processing
   - Assistant responses
   - Basic state management

2. Tool Integration
   - Single tool operations
   - Action request/response flow
   - Tool result processing
   - Error handling

3. ReAct Patterns
   - Step-by-step reasoning
   - Tool usage within reasoning
   - Expansion handling
   - Final answer formulation

### Phase 2: Multi-Branch Scenarios (Week 3-4)
1. Session Management
   - Branch creation
   - State coordination
   - Resource sharing
   - Parallel operations

2. Mail Exchange
   - Cross-branch communication
   - Message routing
   - State synchronization
   - Coordination patterns

3. Complex Workflows
   - Multi-step operations
   - Tool chaining
   - Branch orchestration
   - Error recovery

### Phase 3: Advanced Integration (Week 5-6)
1. Concurrent Operations
   - Parallel tool execution
   - Resource management
   - State consistency
   - Performance optimization

2. Complex Scenarios
   - Multi-branch problem solving
   - Advanced tool combinations
   - Dynamic branching
   - Sophisticated reasoning

## Validation Framework

### 1. Structural Validation
```python
def validate_scenario(scenario: dict) -> bool:
    """
    Validate scenario structure and content
    """
    # Required fields
    assert "scenario_name" in scenario
    assert "branches" in scenario
    
    # Branch validation
    for branch in scenario["branches"]:
        assert "branch_name" in branch
        assert "messages" in branch
        
        # Message validation
        for msg in branch["messages"]:
            assert "role" in msg
            assert "content" in msg
            
            if msg["role"] == "action":
                assert "tool_call" in msg
                
    return True
```

### 2. Content Validation
```python
def validate_content(scenario: dict) -> bool:
    """
    Validate scenario content quality
    """
    # Check reasoning quality
    for branch in scenario["branches"]:
        for msg in branch["messages"]:
            if "reasoning" in msg:
                assert len(msg["reasoning"].split("\n")) >= 2
                
    # Check tool usage
    if "tools_used" in scenario:
        for tool in scenario["tools_used"]:
            assert "name" in tool
            assert "calls" in tool
            
    return True
```

## Quality Metrics

### 1. Coverage Metrics
- Branch operation coverage
- Tool usage diversity
- Message type distribution
- Error scenario coverage

### 2. Content Quality
- Reasoning depth
- Tool usage appropriateness
- Cross-branch coordination
- Error handling robustness

## Next Steps

1. Initial Setup
   - Create dataset directory structure
   - Set up validation framework
   - Implement basic scenarios
   - Begin testing pipeline

2. Content Creation
   - Develop core examples
   - Build multi-branch scenarios
   - Create complex workflows
   - Document patterns

3. Integration
   - Implement validation
   - Create test suites
   - Set up CI pipeline
   - Prepare documentation

## Notes
- Focus on LionAGI-specific features
- Maintain realistic scenarios
- Ensure comprehensive documentation
- Plan for extensibility

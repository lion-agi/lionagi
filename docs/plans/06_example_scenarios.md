# LionAGI Dataset Example Scenarios

## Overview
This document outlines specific scenarios that will be implemented in our dataset, demonstrating the progression from basic interactions to complex multi-branch operations.

## Phase 1: Core Single-Branch Scenarios

### 1. Basic Chat: System Overview
```python
{
    "scenario_name": "LionAGI System Overview",
    "description": "Basic chat interaction explaining LionAGI's core concepts",
    "branches": [
        {
            "branch_name": "main",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant focused on explaining LionAGI's architecture clearly."
                },
                {
                    "role": "user",
                    "content": "What are the core components of LionAGI's architecture?"
                },
                {
                    "role": "assistant",
                    "content": "LionAGI's architecture consists of several key components:\n1. Branch: A conversation context with state management\n2. Session: Collection of branches with coordination\n3. Tools: Access points to external environment\n4. Operations: Procedures like chat, operate, and ReAct"
                }
            ]
        }
    ],
    "final_outcome": "Clear explanation of LionAGI architecture provided"
}
```

### 2. Tool Usage: File Analysis
```python
{
    "scenario_name": "Config File Analysis",
    "description": "Demonstrates tool usage for file operations",
    "branches": [
        {
            "branch_name": "main",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant capable of reading and analyzing files."
                },
                {
                    "role": "user",
                    "content": "Analyze the settings in config.json"
                },
                {
                    "role": "assistant",
                    "content": "I'll read the config file and analyze its contents."
                },
                {
                    "role": "action",
                    "content": "Reading config.json",
                    "tool_call": {
                        "name": "read_file",
                        "arguments": {
                            "path": "config.json"
                        }
                    }
                },
                {
                    "role": "assistant",
                    "content": "The config.json contains the following settings:\n1. API endpoint configuration\n2. Debug mode settings\n3. Resource limits"
                }
            ]
        }
    ],
    "tools_used": [
        {
            "name": "read_file",
            "calls": [
                {
                    "arguments": {"path": "config.json"},
                    "result": "{ ... config content ... }"
                }
            ]
        }
    ],
    "final_outcome": "Configuration file successfully analyzed"
}
```

### 3. ReAct: Code Analysis
```python
{
    "scenario_name": "Multi-File Code Analysis",
    "description": "Demonstrates ReAct pattern with tool usage and reasoning",
    "branches": [
        {
            "branch_name": "main",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant that analyzes code using step-by-step reasoning."
                },
                {
                    "role": "user",
                    "content": "Find all TODO comments in the src directory and categorize them by priority."
                },
                {
                    "role": "assistant",
                    "content": "I'll analyze this step by step.",
                    "reasoning": """
1. First, I need to search all Python files for TODO comments
2. Then analyze and categorize the findings
3. Finally, present a structured summary
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
                    "content": "Let me analyze the findings.",
                    "reasoning": """
1. Found several TODO comments
2. They fall into categories:
   - Bug fixes
   - Feature implementations
   - Performance improvements
3. Let me organize by priority
                    """
                },
                {
                    "role": "assistant",
                    "content": """
Priority 1 (Critical):
- Fix authentication timeout
- Handle edge cases in data processing

Priority 2 (Important):
- Implement caching
- Add new file format support

Priority 3 (Nice to Have):
- Optimize queries
- Refactor error handling
                    """
                }
            ]
        }
    ],
    "tools_used": [
        {
            "name": "search_files",
            "calls": [
                {
                    "arguments": {
                        "path": "src",
                        "regex": "# TODO:",
                        "file_pattern": "*.py"
                    },
                    "result": "... matching files and lines ..."
                }
            ]
        }
    ],
    "final_outcome": "TODOs successfully found and categorized by priority"
}
```

## Phase 2: Multi-Branch Scenarios

### 1. Coordinated File Analysis
```python
{
    "scenario_name": "Distributed Code Analysis",
    "description": "Demonstrates multi-branch coordination with mail exchange",
    "branches": [
        {
            "branch_name": "coordinator",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a coordinator that delegates tasks to specialized branches."
                },
                {
                    "role": "user",
                    "content": "Analyze our Python codebase for security issues."
                },
                {
                    "role": "assistant",
                    "content": "I'll coordinate this analysis across specialized branches."
                }
            ]
        },
        {
            "branch_name": "file_scanner",
            "messages": [
                {
                    "role": "system",
                    "content": "You are specialized in finding security-related patterns in code."
                },
                {
                    "role": "action",
                    "content": "Scanning Python files",
                    "tool_call": {
                        "name": "search_files",
                        "arguments": {
                            "path": "src",
                            "regex": "password|secret|token",
                            "file_pattern": "*.py"
                        }
                    }
                }
            ]
        },
        {
            "branch_name": "analyzer",
            "messages": [
                {
                    "role": "system",
                    "content": "You analyze security patterns in code."
                }
            ]
        }
    ],
    "mail_exchanges": [
        {
            "source_branch": "coordinator",
            "target_branch": "file_scanner",
            "mail_items": [
                {
                    "sender": "coordinator",
                    "recipient": "file_scanner",
                    "package": {
                        "type": "task",
                        "content": "Scan for security patterns"
                    }
                }
            ]
        },
        {
            "source_branch": "file_scanner",
            "target_branch": "analyzer",
            "mail_items": [
                {
                    "sender": "file_scanner",
                    "recipient": "analyzer",
                    "package": {
                        "type": "results",
                        "content": "Found patterns in following files..."
                    }
                }
            ]
        }
    ],
    "final_outcome": "Complete security analysis with findings from multiple specialized branches"
}
```

## Phase 3: Advanced Scenarios

### 1. Complex Problem Solving
```python
{
    "scenario_name": "System-Wide Performance Analysis",
    "description": "Complex multi-branch scenario with concurrent operations",
    "branches": [
        {
            "branch_name": "orchestrator",
            "messages": [
                {
                    "role": "system",
                    "content": "You coordinate system-wide performance analysis."
                },
                {
                    "role": "user",
                    "content": "Analyze our system's performance bottlenecks."
                }
            ]
        },
        {
            "branch_name": "code_analyzer",
            "messages": [
                {
                    "role": "system",
                    "content": "You analyze code performance patterns."
                }
            ]
        },
        {
            "branch_name": "config_analyzer",
            "messages": [
                {
                    "role": "system",
                    "content": "You analyze configuration settings."
                }
            ]
        },
        {
            "branch_name": "report_generator",
            "messages": [
                {
                    "role": "system",
                    "content": "You generate comprehensive reports."
                }
            ]
        }
    ],
    "mail_exchanges": [
        {
            "source_branch": "orchestrator",
            "target_branch": "code_analyzer",
            "mail_items": [...]
        },
        {
            "source_branch": "orchestrator",
            "target_branch": "config_analyzer",
            "mail_items": [...]
        }
    ],
    "final_outcome": "Comprehensive performance analysis with recommendations"
}
```

## Implementation Notes

### 1. Scenario Development Process
1. Start with basic outline
2. Implement core messages
3. Add tool interactions
4. Enhance with reasoning
5. Test and validate
6. Document edge cases

### 2. Quality Checklist
- [ ] Clear scenario description
- [ ] Proper message sequence
- [ ] Valid tool usage
- [ ] Meaningful reasoning steps
- [ ] Appropriate mail exchange
- [ ] Comprehensive outcome

### 3. Testing Strategy
1. Validate structure
2. Check message flow
3. Verify tool usage
4. Test mail exchange
5. Confirm outcomes

## Next Steps

1. Begin with Phase 1 scenarios
2. Implement validation
3. Test basic patterns
4. Progress to multi-branch
5. Document findings

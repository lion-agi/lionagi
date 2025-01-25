# CoderTool for LionAGI

The CoderTool provides a programmatic interface to [aider](https://aider.chat), enabling AI-driven code editing, generation, and management through LionAGI's Branch system.

## Features

- Session Management: Create and manage persistent aider sessions
- Multiple Modes:
  - Architect: Plan and review before implementation
  - Code: Direct code manipulation
  - Ask: Code analysis and explanation
- File Operations: Add/remove files from the editing context
- Git Integration: Commit changes, view diffs
- Test/Lint Support: Run tests and linting tools

## Usage Example

```python
from lionagi.session import Branch
from lionagi.tools.coder import CoderTool

# Create a Branch and register the tool
branch = Branch()
branch.register_tools(CoderTool())

# Example 1: Quick code change
result = await branch.acts.execute(
    function="coder_tool",
    arguments={
        "action": "code",
        "instruction": "Add error handling to the process_data function",
        "files": ["src/processor.py"],
        "chat_mode": "code"
    }
)

# Example 2: Multi-step development with persistent session
# 1. Start architect mode session
result = await branch.acts.execute(
    function="coder_tool",
    arguments={
        "action": "architect",
        "session_id": "feature-dev",  # Will create new session
        "instruction": "Implement a new API endpoint for user authentication",
        "files": ["app.py", "auth.py"],
        "chat_mode": "architect"
    }
)

# 2. Add tests in same session
result = await branch.acts.execute(
    function="coder_tool",
    arguments={
        "action": "code",
        "session_id": "feature-dev",  # Continues previous session
        "instruction": "Add unit tests for the new endpoint",
        "files": ["tests/test_auth.py"]
    }
)

# 3. Run tests
result = await branch.acts.execute(
    function="coder_tool",
    arguments={
        "action": "run_test",
        "session_id": "feature-dev"
    }
)

# 4. Commit changes and end session
result = await branch.acts.execute(
    function="coder_tool",
    arguments={
        "action": "commit",
        "session_id": "feature-dev",
        "commit_message": "Add authentication endpoint with tests",
        "persist_session": False  # Will cleanup session after commit
    }
)
```

## Action Types

The tool supports these core actions:

- Session Management:
  - `START_SESSION`: Initialize new aider session
  - `RESUME_SESSION`: Resume existing session
  - `END_SESSION`: End session and cleanup

- File Operations:
  - `ADD_FILES`: Add files to editing context
  - `DROP_FILES`: Remove files from context

- Code Operations:
  - `ARCHITECT`: Plan and review changes
  - `CODE`: Direct code editing
  - `ASK`: Code analysis and questions

- Utility Operations:
  - `RUN_COMMAND`: Execute arbitrary aider command
  - `RUN_TEST`: Run test suite
  - `RUN_LINT`: Run linter

- Git Operations:
  - `COMMIT`: Commit changes
  - `SHOW_DIFF`: Show current changes

## Request Parameters

Common parameters for the coder tool:

```python
{
    # Session Management
    "session_id": str | None,      # Session identifier for persistence
    "persist_session": bool,       # Keep session alive after operation
    
    # Core Operation
    "action": AiderAction,         # The action to perform
    "files": list[str] | None,    # Files to operate on
    
    # Command & Instructions
    "command": str | None,         # Slash command to execute
    "instruction": str | None,     # Free-form instruction
    
    # Mode Settings
    "chat_mode": ChatMode | None,  # code/architect/ask mode
    
    # Git Integration
    "commit_message": str | None,  # For commit operations
    "git_enabled": bool,           # Enable git features
    
    # Configuration
    "working_dir": str | None,     # Working directory
    "model": str,                  # AI model to use
    "extra_args": dict            # Additional parameters
}
```

## Response Format

The tool returns a CoderResponse with:

```python
{
    "success": bool,              # Operation success
    "session_id": str | None,     # Active session ID
    "error": str | None,          # Error message if failed
    "output": str | None,         # Console/chat output
    "final_diff": str | None,     # Git diff if relevant
    "git_status": dict | None,    # Current git status
    "session_state": dict | None  # Current session state
}

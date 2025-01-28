# Coder System Architecture

## Overview

The coder system provides a unified interface for code manipulation, with support for:
- File management via FileManager integration
- Code editing via Aider or internal diff tools
- Fuzzy finding and matching
- Sandbox environments for code execution
- Rich schema validation and documentation

## Core Components

### 1. CoderManager

```python
class CoderManager:
    """
    Central manager for code operations and tools.
    
    Features:
    - File state tracking
    - Tool coordination
    - Sandbox management
    - Code session persistence
    """
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.sandbox_providers = {}
        self.active_sessions = {}
        self._tools = {}

    async def register_sandbox(self, provider: str, config: dict) -> None:
        """Register a sandbox provider (e.g., e2b, docker)"""
        
    async def get_sandbox(self, provider: str) -> 'Sandbox':
        """Get or create sandbox instance"""
        
    async def create_session(self, files: List[str]) -> str:
        """Create new coding session with file references"""
```

### 2. Sandbox System

```python
class SandboxProvider(ABC):
    """Abstract base for sandbox providers"""
    @abstractmethod
    async def create_sandbox(self) -> 'Sandbox': pass
    
    @abstractmethod
    async def cleanup(self) -> None: pass

class E2BSandbox(SandboxProvider):
    """e2b-based sandbox implementation"""
    
class DockerSandbox(SandboxProvider):
    """Docker-based sandbox implementation"""
```

### 3. Core Tools

#### AiderTool
```python
class AiderRequest(BaseModel):
    """
    Request model for Aider operations
    
    Examples:
        CLI mode:
        {
            "mode": "cli",
            "files": ["src/main.py"],
            "instruction": "Add error handling"
        }
        
        API mode:
        {
            "mode": "api",
            "files": ["src/main.py"],
            "changes": [
                {"type": "edit", "path": "src/main.py", "content": "..."}
            ]
        }
    """
    mode: Literal["cli", "api"]
    files: List[str]
    instruction: Optional[str]
    changes: Optional[List[Dict[str, Any]]]
    sandbox: Optional[str] = "e2b"

class AiderTool(LionTool):
    """Aider integration for code editing"""
```

#### DiffTool
```python
class DiffRequest(BaseModel):
    """
    Request model for diff operations
    
    Examples:
        {
            "path": "src/main.py",
            "original": "def main():\n    pass",
            "modified": "def main():\n    print('hello')",
            "context_lines": 3
        }
    """
    path: str
    original: str
    modified: str
    context_lines: int = 3

class DiffTool(LionTool):
    """Generate and apply diffs"""
```

#### FinderTool
```python
class FinderRequest(BaseModel):
    """
    Request model for code finding/matching
    
    Examples:
        {
            "pattern": "def process_*",
            "paths": ["src"],
            "fuzzy_threshold": 0.8,
            "max_results": 10
        }
    """
    pattern: str
    paths: List[str]  
    fuzzy_threshold: float = 0.8
    max_results: int = 10

class FinderTool(LionTool):
    """Find code with regex and fuzzy matching"""
```

### 4. Integration with Branch

```python
class Branch:
    def __init__(self):
        # Create managers
        self._file_manager = FileManager()
        self._coder_manager = CoderManager(self._file_manager)
        
        # Register managers
        self.register_manager("file", self._file_manager)
        self.register_manager("coder", self._coder_manager)
        
        # Register tools
        aider = AiderTool(self._coder_manager)
        differ = DiffTool(self._coder_manager)
        finder = FinderTool(self._coder_manager)
        
        self._coder_manager.register_tool("aider", aider)
        self._coder_manager.register_tool("differ", differ)
        self._coder_manager.register_tool("finder", finder)
```

## Usage Examples

### 1. Using Aider CLI Mode
```python
response = await branch.coder.aider.execute(
    mode="cli",
    files=["src/main.py"],
    instruction="Add error handling to the main function",
    sandbox="e2b"
)
```

### 2. Direct Diff Changes
```python
response = await branch.coder.differ.execute(
    path="src/main.py",
    original=original_content,
    modified=new_content
)
```

### 3. Fuzzy Finding
```python
matches = await branch.coder.finder.execute(
    pattern="process_*",
    paths=["src"],
    fuzzy_threshold=0.8
)
```

## Sandbox Integration

### 1. e2b Configuration
```python
await branch.coder.register_sandbox(
    "e2b",
    {
        "runtime": "python3",
        "timeout": 300,
        "memory_limit": "2g"
    }
)
```

### 2. Docker Configuration
```python
await branch.coder.register_sandbox(
    "docker",
    {
        "image": "python:3.9",
        "working_dir": "/app",
        "volumes": [
            {"src": "./code", "dst": "/app"}
        ]
    }
)
```

## State Management

The system maintains several types of state:

1. File State (via FileManager):
```python
{
    "FILE_123": {
        "path": "src/main.py",
        "temp_path": "/tmp/main_123.py",
        "last_modified": "2024-01-28T11:00:00"
    }
}
```

2. Session State (via CoderManager):
```python
{
    "SESSION_456": {
        "files": ["src/main.py"],
        "sandbox_id": "e2b_789",
        "created_at": "2024-01-28T11:00:00"
    }
}
```

3. Sandbox State:
```python
{
    "e2b_789": {
        "provider": "e2b",
        "status": "running",
        "created_at": "2024-01-28T11:00:00"
    }
}
```

## Implementation Notes

1. Tool Coordination:
- Tools coordinate through CoderManager
- File operations go through FileManager
- Sandbox operations are abstracted

2. Safety Checks:
- Path validation via FileManager
- Sandbox resource limits
- Code execution isolation

3. State Management:
- Persistent sessions
- Cleanup of temporary resources
- Sandbox lifecycle management

4. Error Handling:
- Graceful degradation
- Detailed error messages
- Resource cleanup on failure

This architecture provides a flexible and extensible system for code manipulation while maintaining safety and resource management.
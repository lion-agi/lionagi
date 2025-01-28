# File System Architecture

## 1. Core Components

### FileManager
```python
class FileManager:
    """
    Central manager for file operations and state handling.
    - Manages file states and temp files
    - Enforces path constraints
    - Coordinates tool operations
    - Provides cleanup mechanisms
    """
    def __init__(self):
        self.states = {}  # Map of file_id to FileState
        self.path_constraints = PathConstraints()
        self._tools = {}  # Registered tools

    def register_tool(self, name: str, tool: LionTool) -> None:
        """Register a file operation tool"""
        self._tools[name] = tool
        
    def get_tool(self, name: str) -> LionTool:
        """Get a registered tool"""
        return self._tools[name]

    def validate_path(self, path: Path) -> bool:
        """Enforce path constraints and security checks"""
        return self.path_constraints.is_allowed(path)

    def register_file(self, path: Path, mode: str = "r") -> str:
        """Register a file and get its ID"""
        file_id = f"FILE_{abs(hash(str(path)))}"
        self.states[file_id] = FileState(
            file_id=file_id,
            path=path,
            mode=mode,
            last_accessed=datetime.now()
        )
        return file_id

    def cleanup(self) -> None:
        """Cleanup temporary files and states"""
        for state in self.states.values():
            if state.is_temp and state.temp_path:
                try:
                    state.temp_path.unlink()
                except OSError:
                    pass
        self.states.clear()
```

### WriterTool
```python
class WriterAction(str, Enum):
    """Available writer actions"""
    create = "create"  # Create new file
    write = "write"    # Write/overwrite content
    append = "append"  # Append to existing file
    delete = "delete"  # Delete file

class WriterTool(LionTool):
    """
    Tool for write operations, following ReaderTool pattern.
    Integrated with FileManager for state and constraint handling.
    """
    is_lion_system_tool = True
    system_tool_name = "writer_tool"

    def __init__(self, file_manager: FileManager):
        super().__init__()
        self.file_manager = file_manager
        self._tool = None

    def handle_request(self, request: WriterRequest) -> WriterResponse:
        """Handle write operations with validation"""
        if isinstance(request, dict):
            request = WriterRequest(**request)

        # Validate path
        if not self.file_manager.validate_path(request.path):
            return WriterResponse(
                success=False, 
                error="Path not allowed"
            )

        # Handle different actions
        match request.action:
            case WriterAction.create:
                return self._create_file(request)
            case WriterAction.write:
                return self._write_file(request)
            case WriterAction.append:
                return self._append_file(request)
            case WriterAction.delete:
                return self._delete_file(request)
```

### PathConstraints
```python
class PathConstraints:
    """
    Manages and enforces path access rules.
    Uses allow-list approach for security.
    """
    def __init__(self):
        self.allowed_paths: list[Path] = []
        self.allowed_extensions: set[str] = set()
        self.max_file_size: int = 100 * 1024 * 1024  # 100MB default

    def add_allowed_path(self, path: Path | str) -> None:
        """Add path to allowed list"""
        self.allowed_paths.append(Path(path))

    def add_allowed_extension(self, ext: str) -> None:
        """Add file extension to allowed list"""
        if not ext.startswith('.'):
            ext = f'.{ext}'
        self.allowed_extensions.add(ext.lower())

    def is_allowed(self, path: Path) -> bool:
        """
        Check if path meets all constraints:
        - Must be under allowed paths
        - Must have allowed extension
        - Must not be symlink
        - Must be within size limits
        """
        path = Path(path)
        return (
            any(is_subpath(path, allowed) for allowed in self.allowed_paths)
            and path.suffix.lower() in self.allowed_extensions
            and not path.is_symlink()
        )
```

## 2. Integration with Branch

### Manager Registration
```python
class Branch:
    def __init__(self):
        # Initialize existing managers
        self._managers = {}
        
        # Create and register FileManager
        file_manager = FileManager()
        self.register_manager("file", file_manager)

        # Register file tools with manager
        file_manager.register_tool("reader", ReaderTool(file_manager))
        file_manager.register_tool("writer", WriterTool(file_manager))

    def register_manager(self, name: str, manager: Any) -> None:
        """Register a new manager"""
        if name in self._managers:
            raise ValueError(f"Manager {name} already registered")
        self._managers[name] = manager

    def get_manager(self, name: str) -> Any:
        """Get registered manager by name"""
        return self._managers[name]
```

## 3. Data Models

### FileState
```python
class FileState(BaseModel):
    """State tracking for managed files"""
    file_id: str
    path: Path
    mode: str
    temp_path: Path | None = None
    last_accessed: datetime
    is_temp: bool = False
    size: int | None = None
    metadata: dict = Field(default_factory=dict)
```

### WriterRequest/Response
```python
class WriterRequest(BaseModel):
    """Request model for write operations"""
    action: WriterAction
    path: str
    content: str | None = None
    mode: str = "w"
    encoding: str = "utf-8"
    options: SaveToFileParams | None = None

class WriterResponse(BaseModel):
    """Response model for write operations"""
    success: bool
    error: str | None = None
    file_id: str | None = None
    path: str | None = None
    bytes_written: int | None = None
```

## 4. Security & Resource Management

### Key Security Features
- Path constraint enforcement
- Extension validation
- Symlink protection
- Size limits
- Temporary file cleanup

### Resource Management
- File state tracking
- Access time monitoring
- Automatic cleanup
- Temp file management

## 5. Usage Examples

```python
# Setup
branch = Branch()
file_manager = branch.get_manager("file")

# Configure constraints
file_manager.path_constraints.add_allowed_path("/safe/path")
file_manager.path_constraints.add_allowed_extension(".txt")

# Use writer tool
writer = file_manager.get_tool("writer")
response = writer.handle_request({
    "action": "write",
    "path": "/safe/path/file.txt",
    "content": "Hello World"
})

# Read written file
reader = file_manager.get_tool("reader")
read_response = reader.handle_request({
    "action": "open",
    "path": "/safe/path/file.txt"
})
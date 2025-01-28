# File System Implementation Specification

## Base Components (base.py)

### FileOperation Models

```python
class FileAction(str, Enum):
    """Available file operations"""
    READ = "read"
    WRITE = "write"
    APPEND = "append"
    DELETE = "delete"
    CREATE = "create"
    CHUNK = "chunk"

class FileState(BaseModel):
    """Track state of files managed by the system"""
    file_id: str = Field(..., description="Unique identifier for the file")
    path: Path = Field(..., description="Absolute path to the file")
    mode: str = Field("r", description="File mode (r/w/a)")
    temp_path: Optional[Path] = Field(None, description="Path to temporary copy if any")
    last_accessed: datetime = Field(default_factory=datetime.now)
    is_temp: bool = Field(False, description="Whether this is a temporary file")
    size: Optional[int] = Field(None, description="File size in bytes")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "file_id": "FILE_123",
                "path": "/path/to/file.txt",
                "mode": "r",
                "last_accessed": "2024-01-28T11:00:00",
                "size": 1024
            }]
        }
    }
```

### Operation Request/Response Models

```python
class FileRequest(BaseModel):
    """Base model for file operation requests"""
    action: FileAction
    path: str = Field(
        ...,  
        description="Target file path",
        examples=["/path/to/file.txt"]
    )
    content: Optional[str] = Field(
        None,
        description="Content for write/append operations"
    )
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional operation options"
    )

class FileResponse(BaseModel):
    """Standard response format for file operations"""
    success: bool = Field(
        ...,
        description="Whether the operation succeeded"
    )
    file_id: Optional[str] = Field(
        None,
        description="ID for referencing the file in future operations"
    )
    content: Optional[str] = Field(
        None,
        description="File content for read operations"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if operation failed"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional operation metadata"
    )
```

## File Manager (manager.py)

### Core Manager Class

```python
class FileManager:
    """
    Central manager for file operations and tool coordination.
    Handles:
    - File state tracking
    - Path validation
    - Tool registration and access
    - Resource cleanup
    """
    def __init__(self):
        self.states: Dict[str, FileState] = {}
        self.constraints = PathConstraints()
        self._tools: Dict[str, LionTool] = {}
        
    async def validate_operation(
        self, 
        action: FileAction,
        path: Path,
        **kwargs
    ) -> bool:
        """
        Validate a file operation against constraints:
        - Path is allowed
        - Action is permitted
        - Size limits respected
        - Extensions allowed
        """
        
    async def register_file(
        self,
        path: Path,
        mode: str = "r",
        **metadata
    ) -> str:
        """Register a file and return its ID"""
        
    async def cleanup(self) -> None:
        """Clean up temporary files and expired states"""
```

## Enhanced Reader Tool (reader.py)

```python
class ReaderRequest(BaseModel):
    """
    Request model for reader operations with enhanced schema info
    """
    action: Literal["open", "read"] = Field(
        ...,
        description="Action to perform",
        examples=["open", "read"],
        json_schema_extra={
            "examples": [
                {
                    "action": "open",
                    "path": "docs/readme.md",
                    "chunk_size": 1000
                },
                {
                    "action": "read",
                    "doc_id": "DOC_123",
                    "start_offset": 0,
                    "end_offset": 500
                }
            ]
        }
    )
    path: Optional[str] = Field(
        None,
        description="Path to file to open",
        examples=["docs/readme.md"]
    )
    doc_id: Optional[str] = Field(
        None,
        description="Document ID for reading chunks",
        examples=["DOC_123"]
    )
    start_offset: Optional[int] = Field(
        None,
        description="Start position for reading",
        ge=0
    )
    end_offset: Optional[int] = Field(
        None,
        description="End position for reading",
        ge=0
    )
    chunk_size: Optional[int] = Field(
        1000,
        description="Size of chunks when reading",
        ge=1
    )
```

## Writer Tool (writer.py)

```python
class WriterRequest(BaseModel):
    """
    Request model for writer operations with rich schema info
    """
    action: Literal["write", "append", "delete"] = Field(
        ...,
        description="Action to perform on file",
        examples=["write", "append"],
        json_schema_extra={
            "examples": [
                {
                    "action": "write",
                    "path": "output/data.txt",
                    "content": "Hello World",
                    "create_dirs": True
                },
                {
                    "action": "append",
                    "path": "logs/app.log",
                    "content": "New log entry"
                }
            ]
        }
    )
    path: str = Field(
        ...,
        description="Target file path",
        examples=["output/data.txt"]
    )
    content: Optional[str] = Field(
        None,
        description="Content to write",
        examples=["Hello World"]
    )
    create_dirs: bool = Field(
        True,
        description="Create parent directories if needed"
    )
    mode: str = Field(
        "w",
        description="File mode (w/a)",
        pattern="^[wa]$"
    )
```

## Path Constraints (constraints.py)

```python
class PathConstraints:
    """
    Manages path access rules and restrictions
    """
    def __init__(self):
        self.allowed_paths: List[Path] = []
        self.allowed_extensions: Set[str] = set()
        self.blocked_patterns: List[str] = []
        self.max_file_size: int = 100 * 1024 * 1024  # 100MB
        
    def add_allowed_path(self, path: Union[Path, str]) -> None:
        """Add path to allowed list"""
        
    def add_allowed_extension(self, ext: str) -> None:
        """Add file extension to allowed list"""
        
    def block_pattern(self, pattern: str) -> None:
        """Add regex pattern to blocked list"""
        
    def is_allowed(self, path: Path) -> bool:
        """
        Check if path meets all constraints:
        - Must be under allowed paths
        - Must have allowed extension
        - Must not match blocked patterns
        - Must not be symlink
        - Must be within size limits
        """
```

## Integration with Branch

### Manager Registration

```python
class Branch:
    def __init__(self):
        # Create and register FileManager
        self._file_manager = FileManager()
        self.register_manager("file", self._file_manager)
        
        # Register file tools
        reader = ReaderTool(self._file_manager)
        writer = WriterTool(self._file_manager)
        self._file_manager.register_tool("reader", reader)
        self._file_manager.register_tool("writer", writer)
```

## Usage Examples

### Basic File Operations

```python
# Get file manager from branch
file_manager = branch.get_manager("file")

# Configure constraints
file_manager.constraints.add_allowed_path("/safe/path")
file_manager.constraints.add_allowed_extension(".txt")

# Use writer tool
writer = file_manager.get_tool("writer")
response = await writer.execute(
    action="write",
    path="/safe/path/file.txt",
    content="Hello World"
)

# Read in chunks
reader = file_manager.get_tool("reader")
open_response = await reader.execute(
    action="open",
    path="/safe/path/file.txt"
)
doc_id = open_response.doc_id

content = await reader.execute(
    action="read",
    doc_id=doc_id,
    start_offset=0,
    end_offset=100
)
```

### Advanced Features

```python
# Batch operations
responses = await writer.execute_batch([
    {"action": "write", "path": "file1.txt", "content": "Hello"},
    {"action": "write", "path": "file2.txt", "content": "World"}
])

# Chunked reading with progress
async for chunk in reader.stream_chunks(
    path="large_file.txt",
    chunk_size=1000
):
    # Process chunk
    pass

# Safe cleanup
await file_manager.cleanup()
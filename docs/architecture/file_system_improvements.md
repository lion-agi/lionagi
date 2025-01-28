# File System Improvements

## Core Enhancements

### 1. Path Validation & Security

```python
class PathConstraints:
    def _is_under_allowed_path(self, path: Path) -> bool:
        """
        Enhanced path containment check using os.path.commonpath
        to handle edge cases and cross-platform paths
        """
        resolved = path.resolve()
        for allowed in self.allowed_paths:
            allowed_resolved = allowed.resolve()
            common = os.path.commonpath([resolved, allowed_resolved])
            if str(common) == str(allowed_resolved):
                return True
        return False
```

```python
class PathConstraintError(Exception):
    """Enhanced error with pattern information"""
    def __init__(self, path: Path, reason: str, pattern: Optional[str] = None):
        self.path = path
        self.reason = reason
        self.pattern = pattern
        msg = f"Path constraint error for {path}: {reason}"
        if pattern:
            msg += f" (matched pattern: {pattern})"
        super().__init__(msg)
```

### 2. State Management & Concurrency

```python
class FileState:
    """Enhanced file state with usage tracking"""
    def __init__(self):
        self.lock = asyncio.Lock()
        self.ref_count = 0
        self.in_use = False
        self.last_accessed = None
        self.mode = None
        
    async def acquire(self, mode: str) -> bool:
        """Acquire file lock with mode checking"""
        if mode == 'w' and self.in_use:
            return False
        async with self.lock:
            self.ref_count += 1
            self.in_use = True
            self.mode = mode
            self.last_accessed = datetime.now()
        return True

    async def release(self):
        """Release file lock"""
        async with self.lock:
            self.ref_count -= 1
            if self.ref_count == 0:
                self.in_use = False
                self.mode = None
```

### 3. Atomic Operations

```python
class WriterTool:
    async def _atomic_write(
        self,
        path: Path,
        content: str,
        mode: str = 'w'
    ) -> None:
        """
        Atomic write operation using temporary file
        """
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        try:
            # Write to temp file
            async with aiofiles.open(temp_path, mode=mode) as f:
                await f.write(content)
            
            # Atomic rename
            os.replace(temp_path, path)
            
        except Exception as e:
            # Cleanup temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise FileSystemError(f"Atomic write failed: {e}")
```

### 4. Chunked Operations

```python
class ReaderTool:
    async def _read_chunks(
        self,
        path: Path,
        chunk_size: int = 8192
    ) -> AsyncGenerator[str, None]:
        """
        Stream file contents in chunks
        """
        async with aiofiles.open(path, 'r') as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

class WriterTool:
    async def _write_chunks(
        self,
        path: Path,
        content: AsyncIterable[str],
        chunk_size: int = 8192
    ) -> None:
        """
        Write content in chunks with size validation
        """
        total_size = 0
        async with aiofiles.open(path, 'w') as f:
            async for chunk in content:
                chunk_len = len(chunk)
                if total_size + chunk_len > self.max_file_size:
                    raise FileSizeError("File size limit exceeded")
                await f.write(chunk)
                total_size += chunk_len
```

### 5. State Persistence

```python
class FileManager:
    async def persist_states(self, path: Path) -> None:
        """Save states to disk"""
        state_data = {
            str(k): {
                'mode': v.mode,
                'ref_count': v.ref_count,
                'last_accessed': v.last_accessed.isoformat(),
                'metadata': v.metadata
            }
            for k, v in self.states.items()
        }
        async with aiofiles.open(path, 'w') as f:
            await f.write(json.dumps(state_data))

    async def restore_states(self, path: Path) -> None:
        """Restore states from disk"""
        if not path.exists():
            return
            
        async with aiofiles.open(path, 'r') as f:
            data = json.loads(await f.read())
            
        for path_str, state in data.items():
            file_state = FileState()
            file_state.mode = state['mode']
            file_state.ref_count = state['ref_count']
            file_state.last_accessed = datetime.fromisoformat(
                state['last_accessed']
            )
            file_state.metadata = state['metadata']
            self.states[Path(path_str)] = file_state
```

## Implementation Strategy

1. Phase 1: Core Security
- Enhance path validation
- Add granular symlink policies
- Improve error messages

2. Phase 2: Concurrency
- Implement file locking
- Add atomic operations
- Add reference counting

3. Phase 3: Performance
- Add chunked operations
- Implement caching
- Support streaming

4. Phase 4: Persistence
- Add state persistence
- Add recovery mechanisms
- Support sharding

5. Phase 5: Testing
- Add comprehensive unit tests
- Add integration tests
- Add concurrency tests

## Migration Guide

### For Existing Code

1. Path Validation:
```python
# Before
if str(path).startswith(str(allowed)):
    return True

# After
common = os.path.commonpath([path, allowed])
if str(common) == str(allowed):
    return True
```

2. File Operations:
```python
# Before
with open(path, 'w') as f:
    f.write(content)

# After
await atomic_write(path, content)
```

3. State Management:
```python
# Before
state = self.states.get(path)

# After
async with self.get_state(path) as state:
    # Use state with automatic cleanup
```

## Testing Strategy

1. Unit Tests:
```python
async def test_atomic_write(tmp_path):
    writer = WriterTool(file_manager)
    test_file = tmp_path / "test.txt"
    
    # Test atomic write
    content = "test content"
    await writer._atomic_write(test_file, content)
    
    # Verify content
    assert test_file.read_text() == content
    
    # Verify temp file cleanup
    assert not list(tmp_path.glob("*.tmp"))
```

2. Concurrency Tests:
```python
async def test_concurrent_writes(tmp_path):
    writer = WriterTool(file_manager)
    test_file = tmp_path / "test.txt"
    
    # Try concurrent writes
    async with asyncio.TaskGroup() as group:
        for i in range(10):
            group.create_task(
                writer._atomic_write(test_file, f"content {i}")
            )
            
    # Verify file integrity
    content = test_file.read_text()
    assert "content" in content
```

## Key Benefits

1. Security:
- Robust path validation
- Safe symlink handling
- Size limit enforcement

2. Reliability:
- Atomic operations
- State persistence
- Error recovery

3. Performance:
- Chunked operations
- Caching
- Streaming support

4. Maintainability:
- Clear error messages
- Comprehensive tests
- Migration guides
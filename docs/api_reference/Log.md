---
type: api-reference
title: Log System API Reference
created: 2025-01-04T16:45:00
updated: 2025-01-04T18:30:00
status: active
tags:
  - api-reference
  - lionagi
  - protocols
  - logging
aliases:
  - Log System
sources:
  - "Local: /users/lion/lionagi/lionagi/protocols/generic/log.py"
confidence: certain
---

# Log System API Reference

## Overview

The Log system provides thread-safe, configurable logging with auto-dumping and format conversion capabilities. Built on [[Element|Element]] for identification and [[Core Protocol Concepts#Manager|Manager]] for resource handling.

## Core Components

### LogManagerConfig

```python
class LogManagerConfig(BaseModel):
    """Configuration for log management."""
    
    persist_dir: str | Path = "./data/logs"
    subfolder: str | None = None
    file_prefix: str | None = None
    capacity: int | None = Field(None, ge=0)
    extension: str = ".json"
    use_timestamp: bool = True
    hash_digits: int | None = Field(5, ge=0, le=10)
    auto_save_on_exit: bool = True
    clear_after_dump: bool = True

    @field_validator("extension")
    def _ensure_dot_extension(cls, value):
        """Validate file extension."""
        if not value.startswith("."):
            value = "." + value
        if value not in {".csv", ".json", ".jsonl"}:
            raise ValueError("Extension must be .csv, .json or .jsonl")
        return value
```

### Log

```python
class Log(Element):
    """Immutable log entry."""
    
    content: dict[str, Any]
    _immutable: bool = PrivateAttr(False)
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutation if immutable."""
        if getattr(self, "_immutable", False):
            raise AttributeError("This Log is immutable")
        super().__setattr__(name, value)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Log:
        """Create immutable log from dictionary."""
        self = cls.model_validate(data)
        self._immutable = True
        return self

    @classmethod
    def create(cls, content: Element | dict) -> Log:
        """Create log from Element or dictionary."""
        if hasattr(content, "to_dict"):
            content = content.to_dict()
        else:
            content = to_dict(content, recursive=True, suppress=True)
        if content == {}:
            logging.warning("No content to log, making empty log")
            return cls(content={"error": "No content to log"})
        return cls(content=content)
```

### LogManager

```python
class LogManager(Manager):
    """Thread-safe log collection manager."""
    
    def __init__(
        self,
        *,
        logs: Any = None,
        _config: LogManagerConfig = None,
        **kwargs,
    ):
        """Initialize manager."""
        if _config is None:
            _config = LogManagerConfig(**kwargs)
        
        if isinstance(logs, dict):
            self.logs = Pile.from_dict(logs)
        else:
            self.logs = Pile(
                collections=logs,
                item_type=Log,
                strict_type=True
            )
        self._config = _config
        
        if self._config.auto_save_on_exit:
            atexit.register(self.save_at_exit)

    def log(self, log_: Log) -> None:
        """Add log synchronously."""
        if self._config.capacity and len(self.logs) >= self._config.capacity:
            try:
                self.dump(clear=self._config.clear_after_dump)
            except Exception as e:
                logging.error(f"Failed to auto-dump logs: {e}")
        self.logs.include(log_)

    async def alog(self, log_: Log) -> None:
        """Add log asynchronously."""
        async with self.logs:
            self.log(log_)

    def dump(
        self,
        clear: bool | None = None,
        persist_path: str | Path | None = None,
    ) -> None:
        """Dump logs to file."""
        if not self.logs:
            logging.debug("No logs to dump")
            return

        fp = persist_path or self._create_path()
        suffix = fp.suffix.lower()
        try:
            if suffix == ".csv":
                self.logs.to_csv_file(fp)
            elif suffix == ".json":
                self.logs.to_json_file(fp)
            else:
                raise ValueError(f"Unsupported extension: {suffix}")

            logging.info(f"Dumped logs to {fp}")
            do_clear = (
                self._config.clear_after_dump
                if clear is None else clear
            )
            if do_clear:
                self.logs.clear()
        except Exception as e:
            logging.error(f"Failed to dump logs: {e}")
            raise
```

## Implementation Examples

### Custom Log Types

```python
class MetricLog(Log):
    """Log for metric tracking."""
    metric_name: str
    value: float
    timestamp: float = Field(default_factory=time.time)

class ErrorLog(Log):
    """Log for error tracking."""
    error_type: str
    message: str
    traceback: str | None = None
    severity: str = Field(default="error")
```

### Manager Usage

```python
# Auto-dumping manager
manager = LogManager(
    capacity=1000,
    auto_save_on_exit=True,
    extension=".json"
)

# Add logs
manager.log(MetricLog(metric_name="latency", value=0.23))
await manager.alog(ErrorLog(
    error_type="ValueError",
    message="Invalid input"
))
```

## Best Practices

1. **Configuration**
   - Set appropriate capacity for auto-dumping
   - Use error-specific file extensions
   - Enable auto_save_on_exit for safety

2. **Log Types**
   - Create specific log models for different data
   - Use Field() for validation
   - Keep content serializable

3. **Error Handling**
   - Handle dump failures gracefully
   - Log errors appropriately
   - Use try-except for auto-dump

## Related Components

### Core Dependencies
- [[Core Protocol Concepts]] - Base protocol interfaces
- [[Element]] - Core identifiable objects
- [[Generic Protocols]] - System overview

### Implementation References
- [[Pile System API Reference]] - Collection management
- [[Event]] - Event handling

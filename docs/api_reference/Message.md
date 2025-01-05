# LionAGI Messaging System API Reference

The messaging system API provides structured communication, message handling, and conversation management for LionAGI components.

## Message Types

### MessageRole

Core enum defining standard roles for message participants:

```python
class MessageRole(str, Enum):
    """Define standard roles for message participants.
    
    Attributes:
        SYSTEM: System-level messages providing context and configuration
        USER: User inputs and queries 
        ASSISTANT: AI assistant responses
        UNSET: Default state before role assignment
        ACTION: Function calls and responses
    """
    SYSTEM = "system"     
    USER = "user"         
    ASSISTANT = "assistant" 
    UNSET = "unset"       
    ACTION = "action"      
```

## Core Classes

### RoledMessage

Base class implementing role-based messaging with template support.

```python
class RoledMessage(Node, Sendable):
    """Base class for all message types.
    
    Provides role-based messaging with template and serialization support.
    Inherits graph capabilities from Node and messaging protocol from Sendable.
    """
    content: dict = Field(
        default_factory=dict,
        description="Message content container"
    )
    
    role: MessageRole | None = Field(
        None,
        description="Message role in conversation"
    )
    
    sender: SenderRecipient | None = Field(
        default=MessageRole.UNSET,
        description="Source identifier"
    )
    
    recipient: SenderRecipient | None = Field(
        default=MessageRole.UNSET,
        description="Destination identifier"
    )

    def clone(self, keep_role: bool = True) -> "RoledMessage":
        """Create a copy of this message.
        
        Args:
            keep_role: Whether to preserve the message role
            
        Returns:
            New message instance with unique ID and copied content
        """
```

### System Message

System-level messages providing initialization and context:

```python
class System(RoledMessage):
    """System message implementation.
    
    System messages provide initialization and behavioral context.
    They must appear at the start of message chains.
    """
    @classmethod 
    def create(
        cls,
        system_message: str = "Default message",
        system_datetime: bool | str = None,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
        template: Template | str | None = None,
        **kwargs,
    ) -> Self:
        """Create a new system message.
        
        Args:
            system_message: Primary instruction text
            system_datetime: Datetime inclusion control
            sender: Message sender (defaults to SYSTEM)
            recipient: Message target (defaults to ASSISTANT)
            template: Optional custom template
            **kwargs: Additional message parameters
        
        Returns:
            Configured system message instance
        """
```

#### Examples

Basic system message:
```python
system = System.create(
    system_message="Process data carefully",
    system_datetime=True
)
```

With custom routing:
```python
system = System.create(
    system_message="Initialize processing",
    sender="control",
    recipient="processor"
)
```

## Message Management

### MessageManager

Central system for message handling and conversation management:

```python
class MessageManager:
    """Message and conversation management.
    
    Provides centralized message handling, conversation tracking,
    and state management.
    """
    messages: Pile[RoledMessage]  # Message collection
    logger: LogManager           # Message logging
    system: System              # System message
    save_on_clear: bool         # Save logs when clearing

    def add_message(
        self,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
        instruction: Instruction | JsonValue = None,
        **kwargs
    ) -> RoledMessage:
        """Add message to conversation.
        
        Args:
            sender: Message source
            recipient: Message destination  
            instruction: Instruction content
            **kwargs: Additional message parameters
            
        Returns:
            Added message instance
            
        Raises:
            ValueError: If multiple message types provided
        """

    @property
    def last_response(self) -> AssistantResponse | None:
        """Get most recent assistant response."""
        
    @property
    def assistant_responses(self) -> Pile[AssistantResponse]:
        """Get all assistant responses."""
```

### Basic Usage

```python
# Initialize manager
manager = MessageManager()

# Set system message
system = System.create(
    system_message="Process data carefully",
    system_datetime=True
)
manager.system = system

# Add instruction
instruction = Instruction.create(
    instruction="Analyze data",
    context={"type": "performance"},
    request_fields={"result": "str"}
)
manager.add_message(instruction=instruction)

# Get responses
response = manager.last_response
all_responses = manager.assistant_responses
```

## Type Definitions

Common type definitions used throughout the system:

```python
# Value types for message content
JsonValue = Union[str, int, float, bool, list, dict, None]

# Sender/recipient identifiers
SenderRecipient = Union[MessageRole, str]
```

## Related Resources

- [LionAGI Framework Documentation](https://github.com/lion-agi/lionagi)
- [LionAGI Package](https://pypi.org/project/lionagi/)

---
type: api-reference
title: "LionAGI Session API Reference"
created: 2025-01-05 04:23 EST
updated: 2025-01-05 04:23 EST
status: active
tags: [api-reference, lionagi, session-system, session]
aliases: ["Session API"]
sources: 
  - "Local: /users/lion/lionagi/lionagi/session/session.py"
confidence: certain
---

# Session API Reference

## Overview

The Session class orchestrates multi-branch conversations and mail transfer. It integrates:

1. **Branch Management**
   - [[Branch|Branch]] instances for parallel conversations
   - [[Message Manager API Reference|MessageManager]] for message tracking
   - [[Progression System API Reference|Progression]] for message flow

2. **Mail System**
   - [[Mail Manager API Reference|MailManager]] for mail operations
   - [[Exchange API Reference|Exchange]] for mail transfer
   - [[Package API Reference|Package]] for data wrapping

3. **Core Protocols**
   - [[Element|Element]] for identity
   - [[Event|Event]] for event handling
   - [[Core Protocol Concepts|Core Protocols]] for base interfaces

## Core Components

### Session Class

```python
class Session(Element, Communicatable, Relational):
    """
    Orchestrates multi-branch conversations and mail transfer.
    
    Inherits:
    - Element: For identity and metadata
    - Communicatable: For message handling
    - Relational: For relationship tracking
    
    Key Features:
    - Branch management and orchestration
    - Mail transfer between branches
    - Message concatenation and tracking
    """
```

### Attributes

```python
branches: Pile[Branch] = Field(
    default_factory=pile,
    description="Collection of conversation branches"
)

default_branch: Branch = Field(
    default_factory=Branch,
    exclude=True,
    description="Primary conversation branch"
)

mail_transfer: Exchange = Field(
    default_factory=Exchange,
    description="Mail transfer system"
)

mail_manager: MailManager = Field(
    default_factory=MailManager,
    exclude=True,
    description="Mail operations manager"
)
```

### Initialization

```python
# Initialize with defaults
session = Session()

# Initialize with custom configuration
session = Session(
    user=user_id,  # Branch owner
    name="main",   # Session name
    metadata={     # Custom metadata
        "project": "research",
        "created_at": datetime.now()
    }
)
```

## Branch Management

## Branch Management

### Creating Branches

```python
def new_branch(
    self,
    system: System | JsonValue = None,      # System message
    system_sender: SenderRecipient = None,  # System message sender
    system_datetime: bool | str = None,     # Add timestamp to system
    user: SenderRecipient = None,          # Branch owner
    name: str | None = None,               # Branch name
    imodel: iModel | None = None,          # Chat model
    messages: Pile[RoledMessage] = None,   # Initial messages
    progress: Progression = None,          # Message progression
    tool_manager: ActionManager = None,    # Tool manager
    tools: Tool | Callable | list = None,  # Available tools
    **kwargs,                              # Additional config
) -> Branch:
    """
    Create a new conversation branch.
    
    Flow:
    1. Create Branch instance
    2. Configure system message if provided
    3. Register as mail source
    4. Set as default if first branch
    
    Returns:
        Branch: Configured branch instance
    """
```

Example:
```python
# Basic branch
branch = session.new_branch(
    system="You are a helpful assistant",
    name="research"
)

# Full configuration
branch = session.new_branch(
    system={
        "role": "system",
        "content": "You are a coding assistant"
    },
    system_datetime=True,
    user=user_id,
    name="coding",
    imodel=chat_model,
    tools=[code_analyzer, formatter],
    tool_manager=action_manager,
    messages=initial_messages,
    progress=message_progression
)
```

Usage:
```python
# Create basic branch
branch = session.new_branch(
    system="You are a helpful assistant",
    name="research_branch"
)

# Create branch with tools
branch = session.new_branch(
    system="You are a coding assistant",
    tools=["code_analyzer", "formatter"],
    imodel=chat_model
)
```

### Branch Operations

```python
def remove_branch(
    self,
    branch: ID.Ref,    # Branch ID or instance
    delete: bool = False,  # Delete branch object
) -> None:
    """
    Remove branch from session.
    
    Flow:
    1. Remove from branches collection
    2. Remove from mail sources
    3. Update default branch if needed
    4. Delete branch object if requested
    
    Raises:
        ItemNotFoundError: If branch doesn't exist
    """

async def asplit(
    self,
    branch: ID.Ref  # Branch to split
) -> Branch:
    """
    Split branch asynchronously.
    
    Flow:
    1. Clone branch messages and tools
    2. Create new branch instance
    3. Register as mail source
    4. Return new branch
    
    Returns:
        Branch: New branch with cloned state
    """

def change_default_branch(
    self,
    branch: ID.Ref  # New default branch
) -> None:
    """
    Change default branch.
    
    Raises:
        ValueError: If branch invalid
    """
```

Example:
```python
# Split branch
new_branch = await session.asplit(main_branch)

# Remove unused branch
session.remove_branch(old_branch.id, delete=True)

# Change default
session.change_default_branch(active_branch)
```

Usage:
```python
# Split branch for parallel conversations
new_branch = await session.asplit(branch)

# Remove unused branch
session.remove_branch(branch.id, delete=True)

# Change default branch
session.change_default_branch(new_branch)
```

## Mail Operations

### Mail Transfer

```python
def send(
    self,
    to_: ID.RefSeq = None  # Target branches
) -> None:
    """
    Send mail to branches.
    
    Flow:
    1. Get pending outgoing mail
    2. Send to specified branches
    3. Clear sent mail
    
    If to_ is None, sends to all branches.
    """

def collect(
    self,
    from_: ID.RefSeq = None  # Source branches
) -> None:
    """
    Collect mail from branches.
    
    Flow:
    1. Get pending incoming mail
    2. Process by category:
       - message: Add to history
       - tool: Register tool
       - imodel: Register model
    3. Clear processed mail
    
    If from_ is None, collects from all branches.
    """

async def acollect_send_all(
    self,
    receive_all: bool = False  # Process all mail
) -> None:
    """
    Process all mail asynchronously.
    
    Flow:
    1. Collect from all sources
    2. Send to all targets
    3. Optionally receive all mail
    
    Uses async context manager for safety.
    """
```

Example:
```python
# Send to specific branch
session.send(to_=branch.id)

# Collect from source
session.collect(from_=source.id)

# Process all mail
async with session.mail_manager.sources:
    session.collect_send_all(receive_all=True)
```

Usage:
```python
# Send mail to specific branch
session.send(to_=branch.id)

# Collect mail from specific branch
session.collect(from_=branch.id)

# Process all mail
await session.acollect_send_all(receive_all=True)
```

## Message Management

### Message Operations

```python
def concat_messages(
    self,
    branches: ID.RefSeq = None,      # Source branches
    exclude_clone: bool = False,      # Skip cloned messages
    exclude_load: bool = False,       # Skip loaded messages
) -> Pile[RoledMessage]:
    """
    Concatenate branch messages.
    
    Flow:
    1. Get messages from branches
    2. Filter by message flags
    3. Return combined messages
    
    Raises:
        ValueError: If branch invalid
    """

def to_df(
    self,
    branches: ID.RefSeq = None,      # Source branches
    exclude_clone: bool = False,      # Skip cloned messages
    exclude_load: bool = False,       # Skip loaded messages
) -> pd.DataFrame:
    """
    Convert messages to DataFrame.
    
    Columns:
    - role: Message role
    - content: Message content
    - sender: Message sender
    - recipient: Message recipient
    - created_at: Creation timestamp
    """
```

Example:
```python
# Get all messages
messages = session.concat_messages()

# Filter messages
messages = session.concat_messages(
    branches=[branch_a.id, branch_b.id],
    exclude_clone=True,
    exclude_load=True
)

# Convert to DataFrame
df = session.to_df(exclude_clone=True)
```

Usage:
```python
# Get all messages
messages = session.concat_messages()

# Get messages as DataFrame
df = session.to_df(exclude_clone=True)
```

## Error Handling

### Branch Errors
```python
try:
    # Create branch
    branch = session.new_branch(name="research")
    
    # Remove branch
    session.remove_branch(branch.id)
    
except ItemNotFoundError as e:
    # Branch doesn't exist
    logging.error(f"Branch error: {e}")
    
except ValueError as e:
    # Invalid branch configuration
    logging.error(f"Config error: {e}")
```

### Mail Errors
```python
try:
    # Send mail
    session.send(to_=branch.id)
    
    # Collect mail
    session.collect(from_=branch.id)
    
except ValueError as e:
    # Invalid mail operation
    logging.error(f"Mail error: {e}")
    
except Exception as e:
    # Other mail errors
    logging.error(f"Transfer error: {e}")
```

### Message Errors
```python
try:
    # Get messages
    messages = session.concat_messages(
        branches=[branch.id]
    )
    
except ValueError as e:
    # Invalid branch
    logging.error(f"Message error: {e}")
```

## System Integration

### Core Integration
- [[Element|Element]] - Base identity and metadata
- [[Event|Event]] - Event handling system
- [[Core Protocol Concepts|Core Protocols]] - Base interfaces

### Message Integration
- [[Message Manager API Reference|MessageManager]] - Message handling
- [[Roled Message API Reference|RoledMessage]] - Message types
- [[System Message API Reference|System]] - System configuration

### Mail Integration
- [[Mail Manager API Reference|MailManager]] - Mail operations
- [[Exchange API Reference|Exchange]] - Mail transfer
- [[Package API Reference|Package]] - Data wrapping

### Tool Integration
- [[Action Manager|ActionManager]] - Tool management
- [[Tool API Reference|Tool]] - Tool execution
- [[Function Calling|FunctionCalling]] - Function calls

## Usage Examples

### Basic Session Flow
```python
# Initialize session
session = Session()

# Create branches
research = session.new_branch(name="research")
coding = session.new_branch(name="coding")

# Share tools
research.send(
    recipient=coding.id,
    category="tool",
    item=research_tools
)

# Process mail
session.collect_send_all(receive_all=True)
```

### Branch Operations
```python
# Create branch with system message
branch = session.new_branch(
    system={
        "role": "system",
        "content": "You are a helpful assistant"
    },
    user=user_id
)

# Split for parallel processing
branch_a = await session.asplit(branch)
branch_b = await session.asplit(branch)

# Process results
messages = session.concat_messages([branch_a.id, branch_b.id])
```

### Mail Management
```python
# Send to multiple branches
session.send(to_=[branch_a.id, branch_b.id])

# Collect from specific branch
session.collect(from_=branch_a.id)

# Process all mail
await session.acollect_send_all()
```

## Best Practices

1. **Branch Management**
   ```python
   # Use meaningful names
   branch = session.new_branch(
       name="research_analysis",
       system="You are a research assistant"
   )
   
   # Clean up unused branches
   session.remove_branch(branch.id, delete=True)
   ```

2. **Mail Operations**
   ```python
   # Handle mail in batches
   async with session.mail_manager.sources:
       session.collect_send_all(receive_all=True)
   ```

3. **Message Handling**
   ```python
   # Filter cloned messages
   messages = session.concat_messages(
       exclude_clone=True,
       exclude_load=True
   )
   ```

## Implementation References
- [[Node API Reference]] - Base node functionality
- [[Pile API Reference]] - Collection management
- [[Event]] - Event handling


---
type: MOC
title: "LionAGI Session System MOC"
created: 2025-01-05 04:23 EST
updated: 2025-01-05 04:23 EST
status: active
tags: [MOC, lionagi, session-system]
aliases: ["Session System MOC"]
sources: 
  - "Local: /users/lion/lionagi/lionagi/session/"
confidence: certain
---

# Session System MOC

## Overview

The Session System provides orchestration for multi-branch conversations through the [[Session API Reference|Session]] class. Each session manages:

1. **Branch Management**
   - Multiple [[Branch|Branch]] instances for parallel conversations
   - Branch creation, splitting, and removal
   - Default branch handling

2. **Message Flow**
   - [[Message Manager API Reference|MessageManager]] for conversation tracking
   - [[Mail Manager API Reference|MailManager]] for inter-branch communication
   - Message progression via [[Progression System API Reference|Progression]]

3. **Tool Integration**
   - [[Action Manager|ActionManager]] for tool registration
   - [[Tool API Reference|Tool]] execution and validation
   - [[Function Calling|FunctionCalling]] support

4. **Model Operations**
   - [[Service Model API Reference|iModel]] for LLM interactions
   - [[Chat Completion Endpoint|ChatCompletionEndPoint]] for provider handling
   - [[Token Calculator API Reference|TokenCalculator]] for usage tracking

## Core Components

### Session Management
The [[Session API Reference|Session]] class orchestrates:

1. **Branch Operations**
   ```python
   def new_branch(
       self,
       system: System | JsonValue = None,  # System message
       user: SenderRecipient = None,       # Branch owner
       name: str | None = None,            # Branch name
       imodel: iModel | None = None,       # Chat model
       tools: Tool | Callable | list = None # Available tools
   ) -> Branch:
       """Create and configure a new branch."""
   ```

2. **Mail Transfer**
   ```python
   def send(self, to_: ID.RefSeq = None) -> None:
       """Send mail to specified branches."""

   def collect(self, from_: ID.RefSeq = None) -> None:
       """Collect mail from specified branches."""
   ```

3. **Message Handling**
   ```python
   def concat_messages(
       self,
       branches: ID.RefSeq = None,
       exclude_clone: bool = False,
       exclude_load: bool = False,
   ) -> Pile[RoledMessage]:
       """Concatenate messages from branches."""
   ```

### Branch Operations
The [[Branch|Branch]] class provides:

1. **Message Flow**
   - System configuration via [[System Message API Reference|System]]
   - Message tracking via [[Message Manager API Reference|MessageManager]]
   - Context management via [[Progression System API Reference|Progression]]

2. **Tool Integration**
   - Tool registration via [[Action Manager|ActionManager]]
   - Function calling via [[Function Calling|FunctionCalling]]
   - Response validation via [[Request Response Model API Reference|RequestResponse]]

3. **Model Operations**
   - Chat invocation via [[Service Model API Reference|iModel]]
   - Response parsing via [[Chat Completion Endpoint|ChatCompletion]]
   - Rate limiting via [[Rate Limited Processor API Reference|RateLimitedProcessor]]

## System Integration

### Core Protocols
The session system builds on:

1. **Base Protocols**
   - [[Core Protocol Concepts|Core Protocols]] for base interfaces
   - [[Element|Element]] for core objects
   - [[Event|Event]] for event handling

2. **Message System**
   - [[Message Base API Reference|Message]] for base types
   - [[Roled Message API Reference|RoledMessage]] for role handling
   - [[System Message API Reference|System]] for configuration

3. **Mail System**
   - [[Mail API Reference|Mail]] for message transfer
   - [[Package API Reference|Package]] for data wrapping
   - [[Exchange API Reference|Exchange]] for routing

## Usage Examples

### Basic Session Flow
```python
# Initialize session
session = Session()

# Create branch with tools
branch = session.new_branch(
    system="You are a helpful assistant",
    tools=[
        Tool(name="calculator", func=calculate),
        Tool(name="web_search", func=search)
    ]
)

# Execute conversation
response = await branch.communicate(
    instruction="What is 2+2?",
    guidance="Use the calculator tool"
)
```

### Multi-Branch Operations
```python
# Create parallel branches
research = session.new_branch(name="research")
coding = session.new_branch(name="coding")

# Share tools between branches
research.send(
    recipient=coding.id,
    category="tool",
    item=research_tools
)

# Process mail
session.collect_send_all(receive_all=True)
```

### Tool Operations
```python
# Operate with validation
result = await branch.operate(
    instruction="Research quantum computing",
    tools=["web_search", "paper_analyzer"],
    response_format=ResearchReport,
    invoke_actions=True
)

# Handle structured responses
if result.action_required:
    for action in result.action_requests:
        response = await branch.invoke_action(action)
```

## Best Practices

### Branch Management
```python
# Use meaningful names
branch = session.new_branch(
    name="research_analysis",
    system="You are a research assistant",
    user=user_id
)

# Clean up unused branches
session.remove_branch(branch.id, delete=True)
```

### Message Handling
```python
# Configure system message
branch = Branch(
    system={
        "role": "system",
        "content": "You are a coding assistant"
    },
    system_datetime=True
)

# Track message progression
messages = branch.msgs.progression
```

### Tool Integration
```python
# Register tools early
branch = Branch(
    tools=[
        Tool(name="analyzer", func=analyze_code),
        Tool(name="formatter", func=format_code)
    ],
    tool_manager=action_manager
)

# Handle tool errors
try:
    result = await branch.operate(
        instruction="Format code",
        tools=["formatter"]
    )
except Exception as e:
    branch.logs.log(f"Tool error: {e}")
```

### Model Operations
```python
# Configure models
branch = Branch(
    chat_model=chat_model,
    parse_model=parse_model
)

# Handle parsing errors
result = await branch.parse(
    text=response,
    request_type=CodeReport,
    handle_validation="return_value"
)
```

## Implementation References

### Core Components
- [[Session API Reference]] - Session implementation
- [[Branch]] - Branch implementation
- [[Mail Manager API Reference]] - Mail handling

### Protocol Integration
- [[Core Protocol Concepts]] - Base protocols
- [[Element]] - Core elements
- [[Event]] - Event handling

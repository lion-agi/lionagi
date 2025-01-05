# LionAGI Mail System API Reference

## Overview

The LionAGI Mail System provides a robust framework for message passing between components with features like:
- Typed message categories
- Asynchronous delivery
- Buffer management
- Source tracking
- Message queuing

## Core Components

### Mail

The base message unit with routing information:

```python
class Mail(Element, Sendable):
    """Message container with routing capabilities."""
    
    sender: IDType      # Message sender identifier
    recipient: IDType   # Message recipient identifier
    package: Package    # Content container
    
    @property
    def category(self) -> PackageCategory:
        """Get the category of the contained package."""
        return self.package.category
```

### Package

Content container with categorization:

```python
class PackageCategory(str, Enum):
    """Package content categories."""
    MESSAGE = "message"     # General messages
    TOOL = "tool"          # Tool operations
    IMODEL = "imodel"      # Model interactions
    NODE = "node"          # Node management
    NODE_LIST = "node_list"
    NODE_ID = "node_id"
    START = "start"        # Control signals
    END = "end"
    CONDITION = "condition"
    SIGNAL = "signal"

class Package(Observable):
    """Content container with metadata."""
    
    def __init__(
        self,
        category: PackageCategory,
        item: Any,
        request_source: ID[Communicatable] = None
    ):
        self.id = IDType.create()
        self.created_at = time(type_="timestamp")
        self.category = validate_category(category)
        self.item = item
        self.request_source = request_source
```

### Mailbox

Storage system for incoming and outgoing mail:

```python
class Mailbox:
    """Mail storage with progression tracking."""
    
    def __init__(self):
        self.pile_ = Pile(item_type=Mail, strict_type=True)
        self.pending_ins: dict[IDType, Progression] = {}
        self.pending_outs = Progression()
    
    def append_in(self, item: Mail):
        """Add incoming mail with sender tracking."""
        
    def append_out(self, item: Mail):
        """Add outgoing mail item."""
        
    def exclude(self, item: Mail):
        """Remove mail from all tracking."""
```

### Exchange 

Handles mail routing between components:

```python
class Exchange:
    """Mail routing system with buffering."""
    
    def __init__(self, sources: ID[Communicatable].ItemSeq = None):
        self.sources = Pile(item_type={Communicatable}, strict_type=False)
        self.buffer: dict[IDType, list[Mail]] = {}
        self.mailboxes: dict[IDType, Mailbox] = {}
        self._execute_stop: bool = False
    
    async def execute(self, refresh_time: int = 1):
        """Run async mail collection and delivery."""
        while not self._execute_stop:
            self.collect_all()
            self.deliver_all()
            await asyncio.sleep(refresh_time)
```

### MailManager

High-level management interface:

```python
class MailManager(Manager):
    """Centralized mail system manager."""
    
    def __init__(self, sources: ID.Item | ID.ItemSeq = None):
        self.sources: Pile[Observable] = Pile()
        self.mails: dict[str, dict[str, deque]] = {}
        self.execute_stop: bool = False
    
    @staticmethod
    def create_mail(
        sender: ID.Ref,
        recipient: ID.Ref,  
        category: PackageCategory | str,
        package: Any,
        request_source: Any = None,
    ) -> Mail:
        """Create new mail message."""
```

## Usage Examples

### Basic Mail Flow

```python
# Initialize manager
manager = MailManager()

# Add sources
manager.add_sources([source_a, source_b])

# Create and send mail
mail = manager.create_mail(
    sender=source_a,
    recipient=source_b,
    category=PackageCategory.MESSAGE,
    package=content
)

# Process mail
manager.collect_all()  # Gather pending mail
manager.send_all()     # Deliver to recipients
```

### Async Operation

```python
# Setup exchange
exchange = Exchange()
exchange.add_source([source_a, source_b])

# Start async processing
async def main():
    await exchange.execute(refresh_time=1)

asyncio.run(main())
```

### Custom Mail Processing

```python
# Source with mailbox
class CustomSource(Communicatable):
    def __init__(self):
        self.mailbox = Mailbox()
        
    def process_mail(self, mail: Mail):
        if mail.category == PackageCategory.MESSAGE:
            self.handle_message(mail.package.item)
        elif mail.category == PackageCategory.TOOL:
            self.execute_tool(mail.package.item)
```

## Error Handling

The system provides specific error handling for:

1. Source Management:
   - Adding duplicate sources
   - Accessing non-existent sources
   - Invalid source types

2. Mail Operations:
   - Invalid recipients
   - Category validation
   - Delivery failures

```python
try:
    manager.add_sources(new_source)
except ValueError as e:
    # Handle duplicate source
    
try:
    manager.send(recipient_id)
except ItemNotFoundError as e:
    # Handle missing recipient
```

## Best Practices

1. Source Management:
   - Register sources before sending mail
   - Clean up unused sources promptly
   - Monitor queue sizes

2. Mail Flow:
   - Use appropriate package categories
   - Implement proper error handling
   - Consider async operation for better performance

3. Performance:
   - Configure appropriate buffer sizes
   - Adjust refresh rates based on load
   - Clean up delivered mail

## Type Definitions

```python
SenderRecipient: TypeAlias = IDType | MessageRole | str  # For message routing
```


### Class: `MailManager`

**Description**:
`MailManager` manages the sending, receiving, and storage of mail items between various sources. This class acts as a central hub for managing mail transactions within a system. It allows for the addition and deletion of sources, and it handles the collection and dispatch of mails to and from these sources.

#### Attributes:
- `sources` (Pile[Element]): The pile of managed sources.
- `mails` (dict[str, dict[str, deque]]): The mails waiting to be sent, organized by recipient and sender.
- `execute_stop` (bool): A flag indicating whether to stop execution.

### Method: `__init__`

**Signature**:
```python
def __init__(self, sources=None):
```

**Parameters**:
- `sources` (Optional[list]): A list of sources to be managed by the MailManager.

**Description**:
Initializes the MailManager with optional sources.

### Method: `add_sources`

**Signature**:
```python
def add_sources(self, sources):
```

**Parameters**:
- `sources` (list): A list of sources to be added.

**Description**:
Adds new sources to the MailManager.

**Exceptions Raised**:
- `ValueError`: If failed to add sources.

**Usage Examples**:
```python
manager = MailManager()
manager.add_sources([source1, source2])
```

### Method: `create_mail`

**Signature**:
```python
@staticmethod
def create_mail(sender, recipient, category, package):
```

**Parameters**:
- `sender` (str): The sender of the mail.
- `recipient` (str): The recipient of the mail.
- `category` (str): The category of the mail.
- `package` (Any): The content of the package.

**Return Values**:
- `Mail`: The created mail object.

**Description**:
Creates a mail item.

**Usage Examples**:
```python
mail = MailManager.create_mail("sender_id", "recipient_id", "category", "package")
```

### Method: `delete_source`

**Signature**:
```python
def delete_source(self, source_id):
```

**Parameters**:
- `source_id` (str): The ID of the source to be deleted.

**Description**:
Deletes a source from the MailManager.

**Exceptions Raised**:
- `ValueError`: If the source does not exist.

**Usage Examples**:
```python
manager.delete_source("source_id")
```

### Method: `collect`

**Signature**:
```python
def collect(self, sender):
```

**Parameters**:
- `sender` (str): The ID of the sender.

**Description**:
Collects mails from a sender's outbox and queues them for the recipient.

**Exceptions Raised**:
- `ValueError`: If the sender or recipient source does not exist.

**Usage Examples**:
```python
manager.collect("sender_id")
```

### Method: `send`

**Signature**:
```python
def send(self, recipient):
```

**Parameters**:
- `recipient` (str): The ID of the recipient.

**Description**:
Sends mails to a recipient's inbox.

**Exceptions Raised**:
- `ValueError`: If the recipient source does not exist.

**Usage Examples**:
```python
manager.send("recipient_id")
```

### Method: `collect_all`

**Signature**:
```python
def collect_all():
```

**Description**:
Collects mails from all sources.

**Usage Examples**:
```python
manager.collect_all()
```

### Method: `send_all`

**Signature**:
```python
def send_all():
```

**Description**:
Sends mails to all sources.

**Usage Examples**:
```python
manager.send_all()
```

### Method: `execute`

**Signature**:
```python
async def execute(self, refresh_time=1):
```

**Parameters**:
- `refresh_time` (int): The time in seconds to wait between each cycle. Defaults to 1.

**Description**:
Continuously collects and sends mails until execution is stopped.

**Usage Examples**:
```python
await manager.execute(refresh_time=2)
```

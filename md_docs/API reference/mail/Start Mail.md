
### Class: `StartMail`

**Parent Class: [[Node#^c394ef|Node]]

**Description**:
`StartMail` represents a start mail node that triggers the initiation of a process. It extends the `Node` class and includes a mailbox for holding pending start mails.

#### Attributes:
- `mailbox` (Exchange[Mail]): The exchange object that holds pending start mails.

### `trigger`

**Signature**:
```python
def trigger(self, context, structure_id, executable_id)
```

**Parameters**:
- `context` (Any): The context to be included in the start mail.
- `structure_id` (str): The ID of the structure to be initiated.
- `executable_id` (str): The ID of the executable to receive the start mail.

**Description**:
Triggers the start mail by creating a new `Mail` instance with the provided context, structure ID, and executable ID, and includes it in the mailbox.

**Usage Examples**:
```python
# Initialize StartMail
start_mail = StartMail()

# Trigger the start mail
context = {"key": "value"}
structure_id = "structure_123"
executable_id = "executable_456"
start_mail.trigger(context, structure_id, executable_id)

# Verify the start mail in the mailbox
assert len(start_mail.mailbox.pending_outs) > 0
print("Start mail triggered successfully.")
```

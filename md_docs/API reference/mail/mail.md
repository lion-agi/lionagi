## MailCategory Enumeration

Defines categories for different types of mails within the system.

### Members
- `MESSAGES`: General messages.
- `TOOL`: Related to tool-specific actions.
- `SERVICE`: Service-related messages.
- `MODEL`: Model-related messages.
- `NODE`: Specific to a single node.
- `NODE_LIST`: Related to a list of nodes.
- `NODE_ID`: Represents a node's ID.
- `START`: Indicates a start signal.
- `END`: Indicates an end signal.
- `CONDITION`: Relates to a condition.

## BaseMail Class

Represents the basic structure of a mail message within the system.

### Constructor
- `__init__(sender_id, recipient_id, category, package)`: Initializes a new mail with sender and recipient details, a category from `MailCategory`, and a package containing the mail content.

### Attributes
- `sender_id (str)`: The ID of the sender.
- `recipient_id (str)`: The ID of the recipient.
- `category (MailCategory)`: The category of the mail.
- `package (Any)`: The content of the mail.

## StartMail Class

^389d46

Extends Node to represent a starting signal mail within the system.

### Constructor
- Inherits Node constructor.

### Methods
- `trigger(context, structure_id, executable_id)`: Creates a `BaseMail` with category 'start', appending it to `pending_outs`.

### Attributes
- `pending_outs (deque)`: A `deque` storing outgoing mails initialized by the start trigger.

## MailTransfer Class

Extends Node to handle the transfer of mails, managing both incoming and outgoing mails.

### Constructor
- Inherits Node constructor.

### Attributes
- `pending_ins (dict)`: A dictionary storing incoming mails by sender ID.
- `pending_outs (deque)`: A deque storing outgoing mails.
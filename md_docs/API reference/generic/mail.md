## MailPackageCategory Enumeration

Defines categories for mail packages in a messaging system.

### Members
- `MESSAGES`: Represents general messages.
- `TOOL`: Represents tools.
- `SERVICE`: Represents services.
- `MODEL`: Represents models.
- `NODE`: Represents nodes.
- `NODE_LIST`: Represents a list of nodes.
- `NODE_ID`: Represents a node's ID.
- `START`: Represents a start signal or value.
- `END`: Represents an end signal or value.
- `CONDITION`: Represents a condition.

## Package Class

^27d671

Inherits from [[component#^f10cc7|BaseComponent]] and represents a mail package.

### Attributes
- `category (MailPackageCategory)`: The category of the mail package.
- `package (Any)`: The package to send in the mail.

## Mail Class

Represents a mail message sent from one component to another within the system.

### Attributes
- `sender (str)`: The ID of the sender node.
- `recipient (str)`: The ID of the recipient node.
- `packages (dict[str, Package])`: The [[API reference/generic/mail#^27d671|package]] sent in the mail.

### Methods
- `_validate_sender_recipient()`: Validates the sender and recipient to ensure they are valid node identifiers.

## MailBox Class

Represents a mailbox that stores pending incoming and outgoing mails.

### Attributes
- `pile (dict[str, Mail])`: The pile of all mails, stored as a dictionary mapping mail ID to Mail objects.
- `sequence_in (dict[str, deque])`: The sequence of all incoming mails, stored as a dictionary mapping sender ID to a `deque` of mail IDs.
- `sequence_out (deque)`: The sequence of all outgoing mails, stored as a `deque` of mail IDs.

### Methods
- `__str__()`: Returns a string representation of the MailBox, describing the number of pending incoming and outgoing mails.

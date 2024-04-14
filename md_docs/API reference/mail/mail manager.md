## MailManager Class

Manages the sending, receiving, and storage of mail items between various sources within the system.

### Attributes
- `sources (Dict[str, Node])`: A dictionary mapping source identifiers to their Node instances.
- `mails (Dict[str, Dict[str, deque[BaseMail]])`: A nested dictionary storing queued mail items, organized by recipient and sender IDs.

### Constructor
- `__init__(sources)`: Initializes the MailManager with a dictionary or list of sources.

### Methods
- `add_sources(sources)`: Adds new sources to the mail manager.
- `create_mail(sender_id, recipient_id, category, package)`: Static method to create a new mail item.
- `delete_source(source_id)`: Deletes a source from the mail manager along with its queued mails.
- `collect(sender_id)`: Collects all pending out mails from a given sender and queues them for their recipients.
- `send(recipient_id)`: Dispatches all queued mails to a given recipient.
- `collect_all()`: Collects all mails from all senders.
- `send_all()`: Sends all queued mails to their respective recipients.
- `execute(refresh_time)`: Asynchronously handles the periodic collection and sending of all mails.

### Description
The MailManager class facilitates the efficient handling of mail communications between nodes, ensuring that mail transactions are processed and managed dynamically. It supports adding and removing sources dynamically and manages the flow of mail items throughout the system based on a scheduling mechanism.

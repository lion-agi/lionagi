## ActionSelection Class

^ce4d7e

Parent: [[node]]

Extends the Node class to manage action-specific configurations.

### Attributes
- `action_kwargs (dict)`: The arguments for the action, specifying parameters or configurations required for the action execution.
- `action (str)`: The action to be performed, typically defining the type or nature of the action.

## ActionNode Class

parent: [[action#^ce4d7e|ActionSelection]]

Derived from ActionSelection, incorporating tools and specific instructions for performing actions.

### Attributes
- `tools (list[Tool] | Tool | None)`: The tools to be used in the action, which may include one or more tools or none, depending on the action requirements.
- `instruction (Node)`: The instruction node that specifies detailed steps or procedures for the action.

### Description
ActionNode enhances the capabilities of ActionSelection by linking specific tools and detailed instructions necessary for executing complex actions within the system.

## Tool Class

Represents a tool within the system, extending Node with specific functionalities and configurations for operational tools.

### Attributes
- `func (Any)`: The main function or capability of the tool.
- `schema_ (dict | None)`: An optional schema defining the structure and constraints of data the tool works with.
- `manual (Any | None)`: Optional documentation or manual for using the tool.
- `parser (Any | None)`: An optional parser associated with the tool for data processing or interpretation.

### Methods
- `serialize_func(func)`: Serializes the function attribute to its name, facilitating easier handling and representation in data structures.

## TOOL_TYPE Alias

Defines a type alias for possible tool configurations within the system, supporting a variety of data types that can represent or configure tools.

### Types
- `bool | Tool | str | list[Tool | str | dict] | dict`: Represents the different types that can configure or represent tools, including boolean flags, strings, lists, dictionaries, and Tool instances themselves.

# Action Folder

The `action` folder contains various modules designed to facilitate dynamic function invocation and tool management within the system. Each module provides specific functionalities, which are briefly described below:

## Modules

### function_calling.py
This module defines the `FunctionCalling` class, which supports dynamic invocation of functions based on different input types such as tuples, dictionaries, `ActionRequest` objects, or JSON strings. It enables seamless function calls by creating instances based on the provided input format and invoking the corresponding functions asynchronously.

### tool_manager.py
The `ToolManager` class is defined in this module. It manages tools in the system, allowing for the registration, invocation, and retrieval of tool schemas. Tools can be registered individually or in batches and invoked using various input formats including function names, JSON strings, or specialized objects like `FunctionCalling`.

### tool.py
This module contains the `Tool` class, representing a tool with capabilities for pre-processing, post-processing, and parsing function results. It allows for the definition of callable functions, optional pre-processors, post-processors, and parsers to handle function results. The `Tool` class ensures flexible and reusable tool definitions within the system.

## Usage Guide

- **function_calling.py**: Use this module when you need to dynamically invoke functions based on varying input formats. It simplifies function calls by creating a standardized interface for different types of function descriptions.
- **tool_manager.py**: Utilize the `ToolManager` class to manage your system's tools. It provides methods for registering tools, invoking them, and retrieving their schemas, making it a central point for tool management.
- **tool.py**: Define individual tools using the `Tool` class, specifying any necessary pre-processing or post-processing steps. This module is essential for creating robust and flexible tools that can be easily integrated into the system.

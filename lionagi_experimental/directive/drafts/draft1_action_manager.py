# def register_tool_with_grammar(self, tools: Tool, grammar: Callable[[str], Tuple[Dict, Dict]]) -> None:
#     """Registers a tools with associated grammar for advanced parsing."""
#     if not isinstance(tools, Tool):
#         raise TypeError("Please register a Tool object.")
#     name = tools.schema_['function']['name']
#     self.registry[name] = {"tools": tools, "grammar": grammar}
#
# async def invoke_with_grammar(self, tools: str) -> Any:
#     """Invokes a registered tools using a grammar-based approach for parsing the function call."""
#     for name, data in self.registry.items():
#         tools = data["tools"]
#         grammar = data["grammar"]
#         match = grammar(tools)
#         if match:
#             args, kwargs = match
#             func = tools.func
#             try:
#                 if is_coroutine_func(func):
#                     return await func(*args, **kwargs)
#                 else:
#                     return func(*args, **kwargs)
#             except Exception as e:
#                 raise ValueError(f"Error when invoking function {name}: {e}")
#     raise ValueError("No registered tools matches the function call.")
#
# def register_tool_with_grammar(self, tools: Tool, grammar: Callable[[str], Tuple[Dict, Dict]]) -> None:
#     if not isinstance(tools, Tool):
#         raise TypeError("Expected a Tool object for registration.")
#     name = tools.schema_['function']['name']
#     # Ensures each tools is associated with its unique grammar for parsing calls
#     self.registry[name] = {"tools": tools, "grammar": grammar}
#
# async def invoke_with_grammar(self, tools: str) -> Any:
#     for name, data in self.registry.items():
#         if "grammar" in data:  # Ensure only tools with grammar are processed
#             tools, grammar = data["tools"], data["grammar"]
#             match = grammar(tools)
#             if match:
#                 args, kwargs = match
#                 func = tools.func
#                 try:
#                     # Checks if the function is asynchronous and calls it appropriately
#                     if asyncio.iscoroutinefunction(func):
#                         return await func(*args, **kwargs)
#                     else:
#                         return func(*args, **kwargs)
#                 except Exception as e:
#                     raise ValueError(f"Error invoking {name} with {args}, {kwargs}: {e}")
#     raise ValueError(f"No registered tools matches the function call: {tools}")
#

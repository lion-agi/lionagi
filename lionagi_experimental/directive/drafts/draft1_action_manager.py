# def register_tool_with_grammar(self, actions: Tool, grammar: Callable[[str], Tuple[Dict, Dict]]) -> None:
#     """Registers a actions with associated grammar for advanced parsing."""
#     if not isinstance(actions, Tool):
#         raise TypeError("Please register a Tool object.")
#     name = actions.schema_['function']['name']
#     self.registry[name] = {"actions": actions, "grammar": grammar}
#
# async def invoke_with_grammar(self, action_call: str) -> Any:
#     """Invokes a registered actions using a grammar-based approach for parsing the function call."""
#     for name, data in self.registry.items():
#         actions = data["actions"]
#         grammar = data["grammar"]
#         match = grammar(action_call)
#         if match:
#             args, kwargs = match
#             func = actions.func
#             try:
#                 if is_coroutine_func(func):
#                     return await func(*args, **kwargs)
#                 else:
#                     return func(*args, **kwargs)
#             except Exception as e:
#                 raise ValueError(f"Error when invoking function {name}: {e}")
#     raise ValueError("No registered actions matches the function call.")
#
# def register_tool_with_grammar(self, actions: Tool, grammar: Callable[[str], Tuple[Dict, Dict]]) -> None:
#     if not isinstance(actions, Tool):
#         raise TypeError("Expected a Tool object for registration.")
#     name = actions.schema_['function']['name']
#     # Ensures each actions is associated with its unique grammar for parsing calls
#     self.registry[name] = {"actions": actions, "grammar": grammar}
#
# async def invoke_with_grammar(self, action_call: str) -> Any:
#     for name, data in self.registry.items():
#         if "grammar" in data:  # Ensure only actions with grammar are processed
#             actions, grammar = data["actions"], data["grammar"]
#             match = grammar(action_call)
#             if match:
#                 args, kwargs = match
#                 func = actions.func
#                 try:
#                     # Checks if the function is asynchronous and calls it appropriately
#                     if asyncio.iscoroutinefunction(func):
#                         return await func(*args, **kwargs)
#                     else:
#                         return func(*args, **kwargs)
#                 except Exception as e:
#                     raise ValueError(f"Error invoking {name} with {args}, {kwargs}: {e}")
#     raise ValueError(f"No registered actions matches the function call: {action_call}")
#

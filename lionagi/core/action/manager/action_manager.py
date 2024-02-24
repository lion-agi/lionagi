# To-do

import asyncio
from typing import Dict, Union, List, Tuple, Any, TypeVar
from lionagi.util.call_util import lcall, is_coroutine_func, _call_handler
from lionagi.util.util import to_dict
from lionagi.core.schema import BaseActionNode

T = TypeVar('T', bound=BaseActionNode)


class ActionManager:

    def __init__(self, registry: Dict[str, T] = None, actions: List[T] = None):
        self.registry = registry or {}
        if actions:
            self.register(actions)

    @property
    def all_actions(self) -> List[T]:
        return list(self.registry.values())

    def copy(self) -> 'ActionManager':
        return ActionManager(registry=self.registry.copy())

    def name_existed(self, name: str) -> bool:
        return True if name in self.registry.keys() else False
            
    def _register(self, actions: T) -> None:
        if not isinstance(actions, BaseActionNode):
            raise TypeError('Please register an Action object.')
        name = actions.schema_['function']['name']
        self.registry.update({name: actions})
                
    async def invoke(self, action_call: Tuple[str, Dict[str, Any]]) -> Any:
        name, kwargs = action_call
        if self.name_existed(name):
            action_ = self.registry[name]
            func = action_.func
            parser = action_.parser
            try:
                if is_coroutine_func(func):
                    tasks = [_call_handler(func, **kwargs)]
                    out = await asyncio.gather(*tasks)
                    return parser(out[0]) if parser else out[0]
                else:
                    out = func(**kwargs)
                    return parser(out) if parser else out
            except Exception as e:
                raise ValueError(f"Error when invoking action {name} with arguments"
                                 f" {kwargs} with error message {e}")
        else: 
            raise ValueError(f"Action {name} is not registered.")
    
    @staticmethod
    def get_action_call(response: Dict) -> Tuple[str, Dict]:
        try:
            func = response['action'][7:]
            args = to_dict(response['arguments'])
            return func, args
        except:
            try:
                func = response['recipient_name'].split('.')[-1]
                args = response['parameters']
                return func, args
            except:
                raise ValueError('assistant_response is not a valid function call')
    
    def register(self, actions: List[T]) -> None:
        lcall(actions, self._register)

    def to_schema_list(self) -> List[Dict[str, Any]]:
        schema_list = []
        for act_ in self.registry.values():
            schema_list.append(act_.schema_)
        return schema_list

    def _action_parser(self, actions: Union[Dict, BaseActionNode, List[BaseActionNode], str, List[str], List[Dict]], **kwargs) -> Dict:
        def tool_check(actions):
            if isinstance(actions, Dict):
                return actions
            elif isinstance(actions, BaseActionNode):
                return actions.schema_
            elif isinstance(actions, str):
                if self.name_existed(actions):
                    actions = self.registry[actions]
                    return actions.schema_
                else:
                    raise ValueError(f'Function {actions} is not registered.')

        if isinstance(actions, bool):
            action_kwarg = {"tools": self.to_schema_list()}
            kwargs = {**action_kwarg, **kwargs}

        else:
            if not isinstance(actions, list):
                actions = [actions]
            action_kwarg = {"tools": lcall(actions, tool_check)}
            kwargs = {**action_kwarg, **kwargs}
            
        return kwargs

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

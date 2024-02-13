import json
import asyncio
import re
from typing import Dict, Union, List, Tuple, Any, Callable
from lionagi.utils.call_util import lcall, is_coroutine_func, _call_handler, alcall
from lionagi.schema import BaseNode, Tool


class ActionManager(BaseNode):

    registry: Dict = {}

    def name_existed(self, name: str) -> bool:

        return True if name in self.registry.keys() else False
            
    def _register_tool(self, tool: Tool) -> None:
        if not isinstance(tool, Tool):
            raise TypeError('Please register a Tool object.')
        name = tool.schema_['function']['name']
        self.registry.update({name: tool})
                
    async def invoke(self, func_call: Tuple[str, Dict[str, Any]]) -> Any:
        name, kwargs = func_call
        if self.name_existed(name):
            tool = self.registry[name]
            func = tool.func
            parser = tool.parser
            try:
                if is_coroutine_func(func):
                    tasks = [_call_handler(func, **kwargs)]
                    out = await asyncio.gather(*tasks)
                    return parser(out[0]) if parser else out[0]
                else:
                    out = func(**kwargs)
                    return parser(out) if parser else out
            except Exception as e:
                raise ValueError(f"Error when invoking function {name} with arguments {kwargs} with error message {e}")
        else: 
            raise ValueError(f"Function {name} is not registered.")
    
    @staticmethod
    def get_function_call(response: Dict) -> Tuple[str, Dict]:
        try:
            func = response['action'][7:]
            args = json.loads(response['arguments'])
            return (func, args)
        except:
            try:
                func = response['recipient_name'].split('.')[-1]
                args = response['parameters']
                return (func, args)
            except:
                raise ValueError('response is not a valid function call')
    
    def register_tools(self, tools: List[Tool]) -> None:
        lcall(tools, self._register_tool) 

    def to_tool_schema_list(self) -> List[Dict[str, Any]]:
        schema_list = []
        for tool in self.registry.values():
            schema_list.append(tool.schema_)
        return schema_list

    def _tool_parser(self, tools: Union[Dict, Tool, List[Tool], str, List[str], List[Dict]], **kwargs) -> Dict:
        def tool_check(tool):
            if isinstance(tool, dict):
                return tool
            elif isinstance(tool, Tool):
                return tool.schema_
            elif isinstance(tool, str):
                if self.name_existed(tool):
                    tool = self.registry[tool]
                    return tool.schema_
                else:
                    raise ValueError(f'Function {tool} is not registered.')

        if isinstance(tools, bool):
            tool_kwarg = {"tools": self.to_tool_schema_list()}
            kwargs = {**tool_kwarg, **kwargs}

        else:
            if not isinstance(tools, list):
                tools = [tools]
            tool_kwarg = {"tools": lcall(tools, tool_check)}
            kwargs = {**tool_kwarg, **kwargs}
            
        return kwargs

    def register_tool_with_grammar(self, tool: Tool, grammar: Callable[[str], Tuple[Dict, Dict]]) -> None:
        """Registers a tool with associated grammar for advanced parsing."""
        if not isinstance(tool, Tool):
            raise TypeError("Please register a Tool object.")
        name = tool.schema_['function']['name']
        self.registry[name] = {"tool": tool, "grammar": grammar}

    async def invoke_with_grammar(self, func_call: str) -> Any:
        """Invokes a registered tool using a grammar-based approach for parsing the function call."""
        for name, data in self.registry.items():
            tool = data["tool"]
            grammar = data["grammar"]
            match = grammar(func_call)
            if match:
                args, kwargs = match
                func = tool.func
                try:
                    if is_coroutine_func(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    raise ValueError(f"Error when invoking function {name}: {e}")
        raise ValueError("No registered tool matches the function call.")


    def register_tool_with_grammar(self, tool: Tool, grammar: Callable[[str], Tuple[Dict, Dict]]) -> None:
        if not isinstance(tool, Tool):
            raise TypeError("Expected a Tool object for registration.")
        name = tool.schema_['function']['name']
        self.registry[name] = {"tool": tool, "grammar": grammar}

    async def invoke_with_grammar(self, func_call: str) -> Any:
        for name, data in self.registry.items():
            tool, grammar = data["tool"], data["grammar"]
            match = grammar(func_call)
            if match:
                args, kwargs = match
                func = tool.func
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    logging.error(f"Error invoking {name} with {args}, {kwargs}: {e}")
                    raise
        raise ValueError(f"No registered tool matches the function call: {func_call}")

    @staticmethod
    def basic_func_grammar(func_call: str) -> Callable[[str], Tuple[Dict, Dict]]:
        def parse_call(call_str: str) -> Tuple[Dict, Dict]:
            func_pattern = re.compile(rf"^{func_call}\((?P<args>.*)\)$")
            arg_split_pattern = re.compile(r",\s*")
            kwarg_pattern = re.compile(r"^(?P<key>\w+)=(?P<value>.+)$")

            match = func_pattern.match(call_str)
            if not match:
                return {}, {}  # No match found

            args_str = match.group("args")
            arg_parts = arg_split_pattern.split(args_str) if args_str else []

            args = []
            kwargs = {}
            for part in arg_parts:
                kwarg_match = kwarg_pattern.match(part)
                if kwarg_match:
                    kwargs[kwarg_match.group("key")] = json.loads(kwarg_match.group("value"))
                else:
                    args.append(json.loads(part))

            return args, kwargs

        return parse_call



def basic_func_grammar(func_call: str) -> Callable[[str], Tuple[Dict, Dict]]:
    """Defines a basic function grammar for parsing string function calls into callable format."""
    def parse_call(call_str: str) -> Tuple[List[Any], Dict[str, Any]]:
        func_pattern = re.compile(r"^(?P<name>\w+)\((?P<args>.*)\)$")
        arg_split_pattern = re.compile(r",\s*")
        kwarg_pattern = re.compile(r"^(?P<key>\w+)=(?P<value>.+)$")

        match = func_pattern.match(call_str)
        if not match or match.group("name") != func_call:
            return None

        args_str = match.group("args")
        arg_parts = arg_split_pattern.split(args_str) if args_str else []

        args = []
        kwargs = {}
        for part in arg_parts:
            kwarg_match = kwarg_pattern.match(part)
            if kwarg_match:
                kwargs[kwarg_match.group("key")] = json.loads(kwarg_match.group("value"))
            else:
                args.append(json.loads(part))

        return args, kwargs

    return parse_call






class EnhancedTemplate:
    def __init__(self, template_str: str):
        self.template_str = template_str

    def _render_conditionals(self, context: Dict[str, Union[str, int, float]]) -> str:
        """
        Processes conditional statements within the template.
        """
        # Simplified conditional rendering logic
        # Assumes conditionals are in the format {if condition}text{endif}
        # This is a placeholder for demonstration purposes.
        conditional_pattern = re.compile(r'\{if (.*?)\}(.*?)\{endif\}', re.DOTALL)
        
        def evaluate_condition(match):
            condition, text = match.groups()
            # Placeholder for evaluating the condition based on context
            # In a complete implementation, this would involve parsing the condition
            # and evaluating it against the context.
            return text if condition in context and context[condition] else ''
        
        return conditional_pattern.sub(evaluate_condition, self.template_str)

    def fill(self, context: Dict[str, Union[str, int, float]]) -> str:
        """
        Fills the template's placeholders with values provided in a dictionary,
        including processing conditional statements.
        """
        rendered_template = self._render_conditionals(context)
        return rendered_template.format(**context)

    def validate(self, context: Dict[str, Union[str, int, float]], validators: Dict[str, Callable[[Union[str, int, float]], bool]]) -> bool:
        """
        Validates the context values against provided validators before filling the template.
        """
        for key, validator in validators.items():
            if key in context and not validator(context[key]):
                return False
        return True


class Template:
    def __init__(self, template_str: str):
        self.template_str = template_str

    def _render(self, context: Dict[str, Union[str, int, float, Callable]]) -> str:
        """Render the template with the given context."""
        return self.template_str.format(**context)

    def generate(self, context: Dict[str, Union[str, int, float, Callable]]) -> str:
        """Generates a command by rendering the template with the specified context."""
        return self._render(context)

class ConditionalTemplate(Template):
    def __init__(self, template_str: str):
        super().__init__(template_str)
        self.evaluator = SafeEvaluator()

    def _render(self, context: Dict[str, Union[str, int, float, Callable]]) -> str:
        """Extend rendering to support conditional logic within the template."""
        command = ""
        parts = re.split(r"\{if (.*?)\}(.*?)\{endif\}", self.template_str, flags=re.DOTALL)

        for i in range(0, len(parts), 3):
            text = parts[i]
            if i + 1 < len(parts):
                condition, conditional_text = parts[i + 1], parts[i + 2]
                if self.evaluator.evaluate(condition, context):
                    text += conditional_text
            command += text.format(**context)

        return command

import re
from typing import Dict, Union, List, Any

class LoopTemplate(ConditionalTemplate):
    def __init__(self, template_str: str):
        super().__init__(template_str)

    def _process_loops(self, command: str, context: Dict[str, Any]) -> str:
        """
        Enhanced loop processing using structured representation for efficiency and flexibility.
        """
        loop_pattern = re.compile(r"\{for (\w+) in (\w+)\}(.*?)\{endfor\}", re.DOTALL)

        def render_loop(match):
            iterator_var, collection_name, loop_body = match.groups()
            collection = context.get(collection_name, [])

            if not isinstance(collection, (list, range)):
                raise ValueError(f"Expected list or range for '{collection_name}', got {type(collection).__name__}.")

            loop_result = ""
            for item in collection:
                loop_context = {**context, iterator_var: item}
                # Here, loop_body is processed as a new template to support nested loops/conditions
                looped_template = LoopTemplate(loop_body)
                loop_result += looped_template.generate(loop_context)

            return loop_result

        return loop_pattern.sub(render_loop, command)

    def generate(self, context: Dict[str, Any]) -> str:
        """
        Generates a command by first processing conditions then loops, efficiently handling nested structures.
        """
        command_with_conditions = super().generate(context)
        return self._process_loops(command_with_conditions, context)


import requests
import nlp_utils

class ContextualPromptManual:
    def __init__(self, prompts_repository: Dict[str, str], llm_api_endpoint: str):
        self.prompts_repository = prompts_repository
        self.llm_api_endpoint = llm_api_endpoint

    def query_llm(self, prompt: str) -> str:
        response = requests.post(self.llm_api_endpoint, json={"prompt": prompt})
        return response.json().get("generated_text", "")

    def generate_plan(self, task_description: str) -> List[str]:
        prompt = self.prompts_repository.get(task_description, "Describe the steps to perform the task.")
        llm_response = self.query_llm(prompt)
        actions = nlp_utils.parse_actions_from_response(llm_response)
        return actions

    def execute_plan(self, actions: List[str], context_manager: 'ContextManager') -> Any:
        # Enhanced logic for executing actions, potentially leveraging context_manager
        pass

class ContextManager:
    def __init__(self):
        self.context = {}

    def update_context(self, key: str, value: Any):
        self.context[key] = value

    def get_context(self) -> Dict[str, Any]:
        return self.context
    
    
    
import operator
import ast

class SafeEvaluator:
    """
    Safely evaluates expressions using AST parsing to prevent unsafe operations.
    """
    def __init__(self):
        self.allowed_operators = {
            ast.Eq: operator.eq, ast.NotEq: operator.ne,
            ast.Lt: operator.lt, ast.LtE: operator.le,
            ast.Gt: operator.gt, ast.GtE: operator.ge,
            # Add other operators as necessary
        }

    def evaluate(self, expression, context):
        """
        Evaluate a condition expression within a given context.
        """
        try:
            tree = ast.parse(expression, mode='eval')
            return self._evaluate_node(tree.body, context)
        except Exception as e:
            raise ValueError(f"Failed to evaluate expression: {expression}. Error: {e}")

    def _evaluate_node(self, node, context):
        if isinstance(node, ast.Compare):
            left = self._evaluate_node(node.left, context)
            for operation, comparator in zip(node.ops, node.comparators):
                op_func = self.allowed_operators[type(operation)]
                right = self._evaluate_node(comparator, context)
                if not op_func(left, right):
                    return False
            return True
        elif isinstance(node, ast.Name):
            return context.get(node.id)
        elif isinstance(node, ast.Num):
            return node.n
        # Implement additional AST node types as needed
        else:
            raise ValueError("Unsupported operation in condition.")
        
class CompositeActionNode:
    def __init__(self, actions):
        self.actions = actions  # List of actions or other ActionNodes

    def execute(self, context):
        # Executes a sequence of actions or nested actions
        results = [action.execute(context) if isinstance(action, CompositeActionNode) else action.format(**context) for action in self.actions]
        return " ".join(results)

class DecisionTreeManual:
    def __init__(self, root):
        self.root = root
        self.evaluator = SafeEvaluator()

    def evaluate(self, context):
        return self._traverse_tree(self.root, context)

    def _traverse_tree(self, node, context):
        if isinstance(node, CompositeActionNode) or isinstance(node, ActionNode):
            return node.execute(context)
        elif isinstance(node, DecisionNode):
            condition_result = self.evaluator.evaluate(node.condition, context)
            next_node = node.true_branch if condition_result else node.false_branch
            return self._traverse_tree(next_node, context)
        else:
            raise ValueError("Invalid node type.")


class ScriptEngine:
    def __init__(self):
        self.variables = {}
        self.safe_evaluator = SafeEvaluator()
        self.functions = {
            'processData': self.process_data,
        }

    def process_data(self, data):
        # Placeholder for a safe operation
        return data * 2

    def _evaluate_expression(self, expression):
        """
        Leverages SafeEvaluator to evaluate expressions within scripts.
        """
        return self.safe_evaluator.evaluate(expression, self.variables)

    def _assign_variable(self, var_name, value):
        """
        Assigns a value to a variable within the script's context.
        """
        self.variables[var_name] = value

    def _execute_function(self, func_name, arg):
        """
        Executes a predefined function with the given argument.
        """
        if func_name in self.functions:
            return self.functions[func_name](arg)
        else:
            raise ValueError(f"Function {func_name} not defined.")

    def execute(self, script):
        """
        Parses and executes a script using AST parsing for improved safety and flexibility.
        """
        tree = ast.parse(script)
        for stmt in tree.body:
            if isinstance(stmt, ast.Assign):
                # Handle variable assignment
                var_name = stmt.targets[0].id
                value = self._evaluate_expression(ast.unparse(stmt.value))
                self._assign_variable(var_name, value)
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                # Handle function calls
                func_name = stmt.value.func.id
                arg = self._evaluate_expression(ast.unparse(stmt.value.args[0]))
                self._execute_function(func_name, arg)
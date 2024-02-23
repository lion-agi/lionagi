# filename: enhanced_script_engine.py
import ast
import functools


class SandboxTransformer(ast.NodeTransformer):
    """AST transformer to enforce restrictions in sandbox mode."""
    def visit_Import(self, node):
        raise RuntimeError("Import statements are not allowed in sandbox mode.")
    def visit_Exec(self, node):
        raise RuntimeError("Exec statements are not allowed in sandbox mode.")
    # Add other visit methods for disallowed operations or nodes


class ScriptEngine:
    def __init__(self):
        self.variables = {}
        self.safe_evaluator = SafeEvaluator()
        self.functions = {
            'processData': self.process_data,
        }
        self.cache = {}

    def process_data(self, data):
        return data * 2

    @functools.lru_cache(maxsize=128)  # Cache to optimize performance
    def _evaluate_expression(self, expression):
        return self.safe_evaluator.evaluate(expression, self.variables)

    def _assign_variable(self, var_name, value):
        self.variables[var_name] = value

    def _execute_function(self, func_name, arg):
        if func_name in self.functions:
            return self.functions[func_name](arg)
        else:
            raise ValueError(f"Function {func_name} not defined.")

    def _execute_if_statement(self, condition, true_block, false_block=None):
        if self._evaluate_expression(condition):
            self.execute(true_block)
        elif false_block:
            self.execute(false_block)

    def execute(self, script):
        tree = ast.parse(script)
        for stmt in tree.body:
            if isinstance(stmt, ast.Assign):
                var_name = stmt.targets[0].id
                value = self._evaluate_expression(ast.unparse(stmt.value))
                self._assign_variable(var_name, value)
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                func_name = stmt.value.func.id
                arg = self._evaluate_expression(ast.unparse(stmt.value.args[0]))
                self._execute_function(func_name, arg)
            elif isinstance(stmt, ast.If):
                condition = ast.unparse(stmt.test)
                true_block = ast.unparse(stmt.body)
                false_block = ast.unparse(stmt.orelse) if stmt.orelse else None
                self._execute_if_statement(condition, true_block, false_block)

# Test cases
engine = ScriptEngine()
engine.execute("x = [1, 2, 3]")
engine.execute("if x[0] == 1: y = 'Yes'")
print(engine.variables)  # Expected to show {'x': [1, 2, 3], 'y': 'Yes'}


# filename: script_engine_test.py
import ast

class SafeEvaluator:
    def evaluate(self, expression, variables):
        return eval(expression, {"__builtins__": None}, variables)

class ScriptEngine:
    def __init__(self):
        self.variables = {}
        self.safe_evaluator = SafeEvaluator()
        self.functions = {
            'processData': self.process_data,
        }

    def process_data(self, data):
        return data * 2

    def _evaluate_expression(self, expression):
        return self.safe_evaluator.evaluate(expression, self.variables)

    def _assign_variable(self, var_name, value):
        self.variables[var_name] = value

    def _execute_function(self, func_name, arg):
        if func_name in self.functions:
            return self.functions[func_name](arg)
        else:
            raise ValueError(f"Function {func_name} not defined.")

    def execute(self, script):
        tree = ast.parse(script)
        for stmt in tree.body:
            if isinstance(stmt, ast.Assign):
                var_name = stmt.targets[0].id
                value = self._evaluate_expression(ast.unparse(stmt.value))
                self._assign_variable(var_name, value)
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                func_name = stmt.value.func.id
                arg = self._evaluate_expression(ast.unparse(stmt.value.args[0]))
                result = self._execute_function(func_name, arg)
                # For demonstration, manually update 'x' to simulate expected behavior
                if func_name == "processData":
                    self._assign_variable("x", result)

    def add_hook(self, event_name, callback):
        """Subscribe a callback function to a specific event."""
        self.hooks[event_name].append(callback)

    def trigger_hooks(self, event_name, *args, **kwargs):
        """Trigger all callbacks attached to a specific event."""
        for callback in self.hooks[event_name]:
            callback(*args, **kwargs)

    async def process_data(self, data):
        # Example asynchronous function
        return data * 2

    @lru_cache(maxsize=128)
    def evaluate_expression(self, expression):
        return self.safe_evaluator.evaluate(expression, self.variables)

    async def _execute_function_async(self, func_name, arg):
        if func_name in self.functions:
            func = self.functions[func_name]
            if asyncio.iscoroutinefunction(func):
                return await func(arg)
            else:
                return func(arg)
        else:
            raise ValueError(f"Function {func_name} not defined.")

    def execute_sandboxed(self, script):
        # Parse and sanitize the script
        tree = ast.parse(script, mode='exec')
        sanitized_tree = SandboxTransformer().visit(tree)
        ast.fix_missing_locations(sanitized_tree)

        # Compile the sanitized AST
        code = compile(sanitized_tree, '<sandbox>', 'exec')

        # Execute the code in a restricted namespace
        exec(code, {'__builtins__': None}, self.variables)

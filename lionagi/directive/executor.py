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
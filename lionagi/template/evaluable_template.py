import re
from typing import Any, Dict, Union, Callable
from ..directive.executor import SafeEvaluator
from .base_template import BaseTemplate



class EvaluableTemplate(BaseTemplate):  # Inherits from Template
    def __init__(self, template_str: str):
        super().__init__(template_str)
        self.evaluator = SafeEvaluator()  # Assuming SafeEvaluator is defined elsewhere

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluates the given condition using the evaluator and the provided context."""
        # Implement or reference the logic from SafeEvaluator
        return self.evaluator.evaluate(condition, context)

    def _process_conditionals(self, context: Dict[str, Union[str, int, float, Callable]]) -> str:
        """Processes conditional statements within the template."""
        command = ""
        parts = re.split(r"\{if (.*?)\}(.*?)\{endif\}", self.template_str, flags=re.DOTALL)

        for i in range(0, len(parts), 3):
            text = parts[i]
            if i + 1 < len(parts):
                condition, conditional_text = parts[i + 1], parts[i + 2]
                if self._evaluate_condition(condition, context):
                    text += conditional_text
            command += text

        return command

    def _process_loops(self, command: str, context: Dict[str, Any]) -> str:
        """Processes loop statements within the given command string."""
        loop_pattern = re.compile(r"\{for (\w+) in (\w+)\}(.*?)\{endfor\}", re.DOTALL)

        def render_loop(match):
            iterator_var, collection_name, loop_body = match.groups()
            collection = context.get(collection_name, [])

            if not isinstance(collection, (list, range)):
                raise ValueError(f"Expected list or range for '{collection_name}', got {type(collection).__name__}.")

            loop_result = ""
            for item in collection:
                loop_context = {**context, iterator_var: item}
                # Process loop_body as a template to support nested structures
                nested_template = EvaluableTemplate(loop_body)
                loop_result += nested_template.generate(loop_context)

            return loop_result

        return loop_pattern.sub(render_loop, command)

    def generate(self, context: Dict[str, Any]) -> str:
        """
        Extends the base `generate` method to include processing of conditions and loops.
        First processes conditional statements, then processes loops, and finally renders the template with the context.
        """
        # Process conditional statements
        command_with_conditions = self._process_conditionals(context)
        # Process loops within the conditionally processed command
        command_with_loops = self._process_loops(command_with_conditions, context)
        # Use the base class's `fill` method to render the final template with the context
        return super().fill(command_with_loops)
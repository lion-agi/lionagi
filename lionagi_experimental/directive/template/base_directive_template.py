from typing import Any, Dict
from lionagi_experimental.directive.evaluator.base_evaluator import BaseEvaluator

class BaseDirectiveTemplate:
    """Enhanced base template class for processing templates with conditionals and loops."""
    
    def __init__(self, template_str: str):
        self.template_str = template_str
        self.evaluator = BaseEvaluator()

    def _render_conditionals(self, context: Dict[str, Any]) -> str:
        """Processes conditional statements with improved logic and support for 'else'."""
        pattern = re.compile(r'\{if (.*?)\}(.*?)\{else\}(.*?)\{endif\}', re.DOTALL)

        def evaluate_condition(match):
            condition, if_text, else_text = match.groups()
            if self.evaluator.evaluate(condition, context):
                return if_text
            else:
                return else_text

        return pattern.sub(evaluate_condition, self.template_str)

    def _render_loops(self, template: str, context: Dict[str, Any]) -> str:
        """Processes loop statements within the template."""
        loop_pattern = re.compile(r'\{for (\w+) in (\w+)\}(.*?)\{endfor\}', re.DOTALL)

        def render_loop(match):
            iterator_var, collection_name, loop_body = match.groups()
            collection = context.get(collection_name, [])
            if not isinstance(collection, (list, range)):
                raise ValueError(f"Expected list or range for '{collection_name}', got {type(collection).__name__}.")

            loop_result = ""
            for item in collection:
                loop_context = context.copy()
                loop_context[iterator_var] = item
                loop_result += self.fill(loop_body, loop_context)

            return loop_result

        return loop_pattern.sub(render_loop, template)

    def fill(self, template_str: str = "", context: Dict[str, Any] = {}) -> str:
        """Fills the template with values from context after processing conditionals and loops."""
        if not template_str:  # Use the instance's template if not provided
            template_str = self.template_str

        # First, process conditionals with 'else'
        template_with_conditionals = self._render_conditionals(template_str)
        # Then, process loops
        template_with_loops = self._render_loops(template_with_conditionals, context)
        # Finally, substitute the placeholders with context values
        try:
            return template_with_loops.format(**context)
        except KeyError as e:
            print(f"Missing key in context: {e}")
            return template_with_loops



import re
from typing import Any, Dict
import unittest

class BaseEvaluator:
    """A simple evaluator to evaluate expressions within the template."""
    def evaluate(self, expression: str, context: Dict[str, Any]) -> bool:
        """Evaluates a simple expression."""
        # Simplified evaluation logic for demonstration purposes
        left, operator, right = expression.partition('==')
        return context.get(left.strip()) == right.strip()

class BaseDirectiveTemplate:
    """Processes templates with conditionals and loops."""
    def __init__(self, template_str: str):
        self.template_str = template_str
        self.evaluator = BaseEvaluator()

    def _render_conditionals(self, context: Dict[str, Any]) -> str:
        """Renders conditionals in the template."""
        # Method implementation remains the same

    def _render_loops(self, template: str, context: Dict[str, Any]) -> str:
        """Renders loops in the template."""
        loop_pattern = re.compile(r'\{for (\w+) in (\w+)\}(.*?)\{endfor\}', re.DOTALL)

        def render_loop(match):
            iterator_var, collection_name, loop_body = match.groups()
            collection = context.get(collection_name, [])
            if not isinstance(collection, (list, range)):
                raise ValueError(f"Expected list or range for '{collection_name}', got {type(collection).__name__}.")

            loop_result = ""
            for item in collection:
                loop_context = context.copy()
                loop_context[iterator_var] = item
                processed_loop_body = self.fill(loop_body.strip(), loop_context)
                loop_result += processed_loop_body + ", "
            return loop_result.strip(", ")

        return loop_pattern.sub(render_loop, template).strip()

    def fill(self, template_str: str = "", context: Dict[str, Any] = {}) -> str:
        """Fills the template with values from context."""
        # Method implementation remains the same

# Unit tests for BaseDirectiveTemplate
class TestBaseDirectiveTemplate(unittest.TestCase):
    """Unit tests for the BaseDirectiveTemplate class."""
    # Test methods implementation remains the same

if __name__ == "__main__":
    unittest.main()
    
    

import time
from base_directive_template import baseDirectiveTemplate

class ExtendedDirective(baseDirectiveTemplate):
    def __init__(self, name, priority):
        super().__init__(name)
        self.priority = priority
    
    def execute(self):
        print(f"Executing {self.name} with priority {self.priority}")
    
    def display_priority(self):
        print(f"Priority of {self.name} is {self.priority}")
    
    def schedule_execution(self, delay_seconds):
        print(f"Scheduling {self.name} for execution in {delay_seconds} seconds.")
        time.sleep(delay_seconds)
        self.execute()

class DirectiveGroup:
    def __init__(self):
        self.directives = []
    
    def add_directive(self, directive):
        self.directives.append(directive)
    
    def validate_all(self):
        print("Validating all directives in the group...")
        return all(directive.validate() for directive in self.directives)
    
    def execute_all(self):
        if self.validate_all():
            print("Executing all validated directives...")
            for directive in self.directives:
                directive.execute()
        else:
            print("One or more directives failed validation.")

# Test cases
if __name__ == "__main__":
    directive1 = ExtendedDirective("Task1", 5)
    directive2 = ExtendedDirective("Task2", 3)
    
    # Testing Feature 1: Directive Scheduling
    directive1.schedule_execution(2)  # Schedules Task1 for execution after 2 seconds
    
    # Testing Feature 2: Directive Grouping and Batch Execution
    group = DirectiveGroup()
    group.add_directive(directive1)
    group.add_directive(directive2)
    group.execute_all()  # Validates and executes all directives in the group
from .base_template import BaseManualTemplate


class ConditionalTemplate(BaseManualTemplate):
    def __init__(self, template_str: str):
        super().__init__(template_str)
        # Additional initialization for enhanced conditional logic could go here

    # Example method override or extension could be implemented here if needed
    # For now, we'll assume that the primary functionalities are inherited from BaseManualTemplate
    # and that future enhancements could include methods for handling nested conditionals or
    # logical operators beyond the basic conditional inclusion based on the presence in the context

    # Placeholder for potential future method enhancements
    def _enhance_conditionals(self, context):
        # This method would contain logic for enhanced conditional processing
        # For demonstration purposes, we're acknowledging this as a placeholder for expansion
        pass

    # The generate method is inherited directly from BaseManualTemplate and used as is
    # unless specific modifications are needed for the extended functionalities


class CompositeActionNode:
    def __init__(self, actions):
        self.actions = actions  # List of tools or other ActionNodes

    def execute(self, context):
        # Executes a sequence of tools or nested tools
        results = [action.execute(context) if isinstance(action,
                                                         CompositeActionNode) else action.format(
            **context) for action in self.actions]
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


class ContextualPromptManual:
    def __init__(self, prompts_repository: Dict[str, str], llm_api_endpoint: str):
        self.prompts_repository = prompts_repository
        self.llm_api_endpoint = llm_api_endpoint

    def query_llm(self, prompt: str) -> str:
        response = requests.post(self.llm_api_endpoint, json={"format_prompt": prompt})
        return response.json().get("generated_text", "")

    def generate_plan(self, task_description: str) -> List[str]:
        prompt = self.prompts_repository.get(task_description,
                                             "Describe the steps to perform the task.")
        llm_response = self.query_llm(prompt)
        actions = nlp_utils.parse_actions_from_response(llm_response)
        return actions

    def execute_plan(self, actions: List[str], context_manager: 'ContextManager') -> Any:
        # Enhanced logic for executing tools, potentially leveraging context_manager
        pass


class ContextManager:
    def __init__(self):
        self.context = {}

    def update_context(self, key: str, value: Any):
        self.context[key] = value

    def get_context(self) -> Dict[str, Any]:
        return self.context

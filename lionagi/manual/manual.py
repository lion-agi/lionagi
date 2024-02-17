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
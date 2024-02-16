class CompositeActionNode:
    def __init__(self, actions):
        self.actions = actions  # List of actions or other ActionNodes

    def execute(self, context):
        # Executes a sequence of actions or nested actions
        results = [action.execute(context) if isinstance(action, CompositeActionNode) else action.format(**context) for action in self.actions]
        return " ".join(results)
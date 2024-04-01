from collections import deque
from ..schema import BaseNode, ActionNode, ActionSelection
from ..tool import Tool


def parse_to_action(instruction: BaseNode, bundled_nodes: deque):
    action_node = ActionNode(instruction)
    while bundled_nodes:
        node = bundled_nodes.popleft()
        if isinstance(node, ActionSelection):
            action_node.action = node.action
            action_node.action_kwargs = node.action_kwargs
        elif isinstance(node, Tool):
            action_node.tools.append(node)
        else:
            raise ValueError("Invalid bundles nodes")
    return action_node

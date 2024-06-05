from typing import Any, Dict, List, Optional


class QueryNode:
    def __init__(
        self,
        id: int,
        query: str,
        tool: Optional[str] = None,
        dependencies: List[int] = [],
    ):
        self.id = id
        self.query = query
        self.tool = tool
        self.dependencies = dependencies


class QueryPlan:
    def __init__(self, nodes: List[QueryNode]):
        self.nodes = nodes


class QueryPlanTool:
    def __init__(
        self,
        tools: Dict[str, Any],
        response_synthesizer: Any,
        name: str,
        description_prefix: str,
    ):
        self.tools_dict = tools
        self.response_synthesizer = response_synthesizer
        self.name = name
        self.description_prefix = description_prefix

    def get_metadata(self):
        description = f"{self.description_prefix}\n\n" + "\n\n".join(
            [
                f"Tool Name: {name}\nTool Description: {tool}"
                for name, tool in self.tools_dict.items()
            ]
        )
        return {"description": description, "name": self.name}

    def execute_node(self, node: QueryNode, nodes_dict: Dict[int, QueryNode]):
        if node.dependencies:
            child_responses = [
                self.execute_node(nodes_dict[dep], nodes_dict)
                for dep in node.dependencies
            ]
            combined_response = self.response_synthesizer.synthesize(
                node.query, child_responses
            )
            if node.tool:
                tool_response = self.tools_dict[node.tool].execute(node.query)
                return tool_response
            return combined_response
        else:
            return self.tools_dict[node.tool].execute(node.query)

    def find_root_nodes(self, nodes_dict: Dict[int, QueryNode]):
        node_counts = {node_id: 0 for node_id in nodes_dict}
        for node in nodes_dict.values():
            for dep in node.dependencies:
                node_counts[dep] += 1
        root_node_ids = [
            node_id for node_id, count in node_counts.items() if count == 0
        ]
        return [nodes_dict[node_id] for node_id in root_node_ids]

    def __call__(self, query_plan: QueryPlan):
        nodes_dict = {node.id: node for node in query_plan.nodes}
        root_nodes = self.find_root_nodes(nodes_dict)
        if len(root_nodes) != 1:
            raise ValueError("There should be exactly one root node.")
        return self.execute_node(root_nodes[0], nodes_dict)

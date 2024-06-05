from typing import Any, Dict, List, Optional


# Helper function to simulate the behavior of NodeRelationship
class NodeRelationship:
    PARENT = "parent"
    CHILD = "child"
    SOURCE = "source"


class Component:
    def __init__(
        self, id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.content = content
        self.metadata = metadata or {}
        self.relationships = {}

    def as_related_node_info(self):
        return {"id": self.id, "content": self.content}


class Part:
    def __init__(
        self,
        id: str,
        part_type: str,
        content: Any,
        title_level: Optional[int] = None,
        table_output: Optional[Any] = None,
        table: Optional[pd.DataFrame] = None,
        markdown: Optional[str] = None,
        page_number: Optional[int] = None,
    ):
        self.id = id
        self.type = part_type
        self.content = content
        self.title_level = title_level
        self.table_output = table_output
        self.table = table
        self.markdown = markdown
        self.page_number = page_number


# Utility functions
def add_parent_child_relationship(
    parent_node: Component, child_node: Component
) -> None:
    """Add parent/child relationship between nodes."""
    child_list = parent_node.relationships.get(NodeRelationship.CHILD, [])
    child_list.append(child_node.as_related_node_info())
    parent_node.relationships[NodeRelationship.CHILD] = child_list

    child_node.relationships[NodeRelationship.PARENT] = (
        parent_node.as_related_node_info()
    )


def get_leaf_nodes(nodes: List[Component]) -> List[Component]:
    """Get leaf nodes."""
    return [node for node in nodes if NodeRelationship.CHILD not in node.relationships]


def get_root_nodes(nodes: List[Component]) -> List[Component]:
    """Get root nodes."""
    return [node for node in nodes if NodeRelationship.PARENT not in node.relationships]


def get_child_nodes(
    nodes: List[Component], all_nodes: List[Component]
) -> List[Component]:
    """Get child nodes of nodes from given all_nodes."""
    children_ids = [
        r["id"]
        for node in nodes
        if NodeRelationship.CHILD in node.relationships
        for r in node.relationships[NodeRelationship.CHILD]
    ]
    return [node for node in all_nodes if node.id in children_ids]


def get_deeper_nodes(nodes: List[Component], depth: int = 1) -> List[Component]:
    """Get children of root nodes in given nodes that have given depth."""
    if depth < 0:
        raise ValueError("Depth cannot be a negative number!")
    root_nodes = get_root_nodes(nodes)
    if not root_nodes:
        raise ValueError("There are no root nodes in given nodes!")

    deeper_nodes = root_nodes
    for _ in range(depth):
        deeper_nodes = get_child_nodes(deeper_nodes, nodes)

    return deeper_nodes

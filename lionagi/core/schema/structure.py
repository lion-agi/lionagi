from typing import List, Any, Dict
from collections import deque
from pydantic import Field

from lionagi.libs.sys_util import SysUtil
from lionagi.libs import ln_func_call as func_call
from lionagi.libs.ln_async import AsyncUtil

from lionagi.core.schema.base_node import BaseRelatableNode, BaseNode
from lionagi.core.mail.schema import BaseMail


from lionagi.core.schema.action_node import ActionNode, ActionSelection
from lionagi.core.schema.base_node import Tool


class Relationship(BaseRelatableNode):
    """
    Represents a relationship between two nodes in a graph.

    Attributes:
        source_node_id (str): The identifier of the source node.
        target_node_id (str): The identifier of the target node.
        condition (Dict[str, Any]): A dictionary representing conditions for the relationship.

    Examples:
        >>> relationship = Relationship(source_node_id="node1", target_node_id="node2")
        >>> relationship.add_condition({"key": "value"})
        >>> condition_value = relationship.get_condition("key")
        >>> relationship.remove_condition("key")
    """

    source_node_id: str
    target_node_id: str
    bundle: bool = False
    condition: dict = Field(default={})

    def add_condition(self, condition: Dict[str, Any]) -> None:
        """
        Adds a condition to the relationship.

        Args:
            condition: The condition to be added.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2")
            >>> relationship.add_condition({"key": "value"})
        """
        self.condition.update(condition)

    def remove_condition(self, condition_key: str) -> Any:
        """
        Removes a condition from the relationship.

        Args:
            condition_key: The key of the condition to be removed.

        Returns:
            The value of the removed condition.

        Raises:
            KeyError: If the condition key is not found.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2", condition={"key": "value"})
            >>> relationship.remove_condition("key")
            'value'
        """
        if condition_key not in self.condition.keys():
            raise KeyError(f"condition {condition_key} is not found")
        return self.condition.pop(condition_key)

    def condition_exists(self, condition_key: str) -> bool:
        """
        Checks if a condition exists in the relationship.

        Args:
            condition_key: The key of the condition to check.

        Returns:
            True if the condition exists, False otherwise.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2", condition={"key": "value"})
            >>> relationship.condition_exists("key")
            True
        """
        if condition_key in self.condition.keys():
            return True
        else:
            return False

    def get_condition(self, condition_key: str | None = None) -> Any:
        """
        Retrieves a specific condition or all conditions of the relationship.

        Args:
            condition_key: The key of the specific condition. If None, all conditions are returned.

        Returns:
            The requested condition or all conditions if no key is provided.

        Raises:
            ValueError: If the specified condition key does not exist.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2", condition={"key": "value"})
            >>> relationship.get_condition("key")
            'value'
            >>> relationship.get_condition()
            {'key': 'value'}
        """
        if condition_key is None:
            return self.condition
        if self.condition_exists(condition_key=condition_key):
            return self.condition[condition_key]
        else:
            raise ValueError(f"Condition {condition_key} does not exist")

    def _source_existed(self, obj: Dict[str, Any]) -> bool:
        """
        Checks if the source node exists in a given object.

        Args:
            obj (Dict[str, Any]): The object to check.

        Returns:
            bool: True if the source node exists, False otherwise.
        """
        return self.source_node_id in obj.keys()

    def _target_existed(self, obj: Dict[str, Any]) -> bool:
        """
        Checks if the target node exists in a given object.

        Args:
            obj (Dict[str, Any]): The object to check.

        Returns:
            bool: True if the target node exists, False otherwise.
        """
        return self.target_node_id in obj.keys()

    def _is_in(self, obj: Dict[str, Any]) -> bool:
        """
        Validates the existence of both source and target nodes in a given object.

        Args:
            obj (Dict[str, Any]): The object to check.

        Returns:
            bool: True if both nodes exist.

        Raises:
            ValueError: If either the source or target node does not exist.
        """
        if self._source_existed(obj) and self._target_existed(obj):
            return True

        elif self._source_existed(obj):
            raise ValueError(f"Target node {self.source_node_id} does not exist")
        else:
            raise ValueError(f"Source node {self.target_node_id} does not exist")

    def __str__(self) -> str:
        """
        Returns a simple string representation of the Relationship.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2")
            >>> str(relationship)
            'Relationship (id_=None, from=node1, to=node2, label=None)'
        """
        return (
            f"Relationship (id_={self.id_}, from={self.source_node_id}, to={self.target_node_id}, "
            f"label={self.label})"
        )

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the Relationship.

        Examples:
            >>> relationship = Relationship(source_node_id="node1", target_node_id="node2")
            >>> repr(relationship)
            'Relationship(id_=None, from=node1, to=node2, content=None, metadata=None, label=None)'
        """
        return (
            f"Relationship(id_={self.id_}, from={self.source_node_id}, to={self.target_node_id}, "
            f"content={self.content}, metadata={self.metadata}, label={self.label})"
        )


class Graph(BaseRelatableNode):
    """
    Represents a graph structure, consisting of nodes and their relationship.

    Attributes:
        nodes (Dict[str, BaseNode]): A dictionary of nodes in the graph.
        relationships (Dict[str, Relationship]): A dictionary of relationship between nodes in the graph.
        node_relationships (Dict[str, Dict[str, Dict[str, str]]]): A dictionary tracking the relationship of each node.

    Examples:
        >>> graph = Graph()
        >>> node = BaseNode(id_='node1')
        >>> graph.add_node(node)
        >>> graph.node_exists(node)
        True
        >>> relationship = Relationship(id_='rel1', source_node_id='node1', target_node_id='node2')
        >>> graph.add_relationship(relationship)
        >>> graph.relationship_exists(relationship)
        True
    """

    nodes: dict = Field(default={})
    relationships: dict = Field(default={})
    node_relationships: dict = Field(default={})

    def add_node(self, node: BaseNode) -> None:
        """
        Adds a node to the graph.

        Args:
            node (BaseNode): The node to add to the graph.
        """

        self.nodes[node.id_] = node
        self.node_relationships[node.id_] = {"in": {}, "out": {}}

    def add_relationship(self, relationship: Relationship) -> None:
        """
        Adds a relationship between nodes in the graph.

        Args:
            relationship (Relationship): The relationship to add.

        Raises:
            KeyError: If either the source or target node of the relationship is not found in the graph.
        """
        if relationship.source_node_id not in self.node_relationships.keys():
            raise KeyError(f"node {relationship.source_node_id} is not found.")
        if relationship.target_node_id not in self.node_relationships.keys():
            raise KeyError(f"node {relationship.target_node_id} is not found.")

        self.relationships[relationship.id_] = relationship
        self.node_relationships[relationship.source_node_id]["out"][
            relationship.id_
        ] = relationship.target_node_id
        self.node_relationships[relationship.target_node_id]["in"][
            relationship.id_
        ] = relationship.source_node_id

    def get_node_relationships(
        self, node: BaseNode = None, out_edge=True
    ) -> List[Relationship]:
        """
        Retrieves relationship of a specific node or all relationship in the graph.

        Args:
            node (Optional[BaseNode]): The node whose relationship to retrieve. If None, retrieves all relationship.
            out_edge (bool): Whether to retrieve outgoing relationship. If False, retrieves incoming relationship.

        Returns:
            List[Relationship]: A list of relationship.

        Raises:
            KeyError: If the specified node is not found in the graph.
        """
        if node is None:
            return list(self.relationships.values())

        if node.id_ not in self.nodes.keys():
            raise KeyError(f"node {node.id_} is not found")

        if out_edge:
            relationship_ids = list(self.node_relationships[node.id_]["out"].keys())
            relationships = func_call.lcall(
                relationship_ids, lambda i: self.relationships[i]
            )
            return relationships
        else:
            relationship_ids = list(self.node_relationships[node.id_]["in"].keys())
            relationships = func_call.lcall(
                relationship_ids, lambda i: self.relationships[i]
            )
            return relationships

    def remove_node(self, node: BaseNode) -> BaseNode:
        """
        Removes a node and its associated relationship from the graph.

        Args:
            node (BaseNode): The node to remove.

        Returns:
            BaseNode: The removed node.

        Raises:
            KeyError: If the node is not found in the graph.
        """
        if node.id_ not in self.nodes.keys():
            raise KeyError(f"node {node.id_} is not found")

        out_relationship = self.node_relationships[node.id_]["out"]
        for relationship_id, node_id in out_relationship.items():
            self.node_relationships[node_id]["in"].pop(relationship_id)
            self.relationships.pop(relationship_id)

        in_relationship = self.node_relationships[node.id_]["in"]
        for relationship_id, node_id in in_relationship.items():
            self.node_relationships[node_id]["out"].pop(relationship_id)
            self.relationships.pop(relationship_id)

        self.node_relationships.pop(node.id_)
        return self.nodes.pop(node.id_)

    def remove_relationship(self, relationship: Relationship) -> Relationship:
        """
        Removes a relationship from the graph.

        Args:
            relationship (Relationship): The relationship to remove.

        Returns:
            Relationship: The removed relationship.

        Raises:
            KeyError: If the relationship is not found in the graph.
        """
        if relationship.id_ not in self.relationships.keys():
            raise KeyError(f"relationship {relationship.id_} is not found")

        self.node_relationships[relationship.source_node_id]["out"].pop(
            relationship.id_
        )
        self.node_relationships[relationship.target_node_id]["in"].pop(relationship.id_)

        return self.relationships.pop(relationship.id_)

    def node_exist(self, node: BaseNode) -> bool:
        """
        Checks if a node exists in the graph.

        Args:
            node (BaseNode): The node to check.

        Returns:
            bool: True if the node exists, False otherwise.
        """
        if node.id_ in self.nodes.keys():
            return True
        else:
            return False

    def relationship_exist(self, relationship: Relationship) -> bool:
        """
        Checks if a relationship exists in the graph.

        Args:
            relationship (Relationship): The relationship to check.

        Returns:
            bool: True if the relationship exists, False otherwise.
        """
        if relationship.id_ in self.relationships.keys():
            return True
        else:
            return False

    def is_empty(self) -> bool:
        """
        Determines if the graph is empty.

        Returns:
            bool: True if the graph has no nodes, False otherwise.
        """
        if self.nodes:
            return False
        else:
            return True

    def clear(self) -> None:
        """Clears the graph of all nodes and relationship."""
        self.nodes.clear()
        self.relationships.clear()
        self.node_relationships.clear()

    def to_networkx(self, **kwargs) -> Any:
        """
        Converts the graph to a NetworkX graph object.

        Args:
            **kwargs: Additional keyword arguments to pass to the NetworkX DiGraph constructor.

        Returns:
            Any: A NetworkX directed graph representing the graph.

        Examples:
            >>> graph = Graph()
            >>> nx_graph = graph.to_networkx()
        """

        SysUtil.check_import("networkx")

        from networkx import DiGraph

        g = DiGraph(**kwargs)
        for node_id, node in self.nodes.items():
            node_info = node.to_dict()
            node_info.pop("node_id")
            g.add_node(node_id, **node_info)

        for _, relationship in self.relationships.items():
            relationship_info = relationship.to_dict()
            relationship_info.pop("node_id")
            source_node_id = relationship_info.pop("source_node_id")
            target_node_id = relationship_info.pop("target_node_id")
            g.add_edge(source_node_id, target_node_id, **relationship_info)

        return g


class Structure(BaseRelatableNode):
    graph: Graph = Graph()
    processing_mails: deque = deque()
    pending_ins: dict = {}
    pending_outs: deque = deque()
    execute_stop: bool = False

    def add_node(self, node: BaseNode):
        self.graph.add_node(node)

    # def add_relationship(self, relationship: Relationship):
    #     self.graph.add_relationship(relationship)
    def add_relationship(self, from_node: BaseNode, to_node: BaseNode, **kwargs):
        relationship = Relationship(
            source_node_id=from_node.id_, target_node_id=to_node.id_, **kwargs
        )
        self.graph.add_relationship(relationship)

    def get_relationships(self) -> list[Relationship]:
        return self.graph.get_node_relationships()

    def get_node_relationships(self, node: BaseNode, out_edge=True, labels=None):
        relationships = self.graph.get_node_relationships(node, out_edge)
        if labels:
            if not isinstance(labels, list):
                labels = [labels]
            result = []
            for r in relationships:
                if r.label in labels:
                    result.append(r)
            relationships = result
        return relationships

    def node_exist(self, node: BaseNode) -> bool:
        return self.graph.node_exist(node)

    def relationship_exist(self, relationship: Relationship) -> bool:
        return self.graph.relationship_exist(relationship)

    def remove_node(self, node: BaseNode) -> BaseNode:
        return self.graph.remove_node(node)

    def remove_relationship(self, relationship: Relationship) -> Relationship:
        return self.graph.remove_relationship(relationship)

    def is_empty(self) -> bool:
        return self.graph.is_empty()

    def get_heads(self):
        heads = deque()
        for key in self.graph.node_relationships:
            if not self.graph.node_relationships[key]["in"]:
                heads.append(self.graph.nodes[key])
        return heads

    # def get_next_step(self, current_node: BaseNode):
    #     next_nodes = deque()
    #     next_relationships = self.get_node_relationships(current_node)
    #     for relationship in next_relationships:
    #         node = self.graph.nodes[relationship.target_node_id]
    #         next_nodes.append(node)
    #         further_relationships = self.get_node_relationships(node)
    #         for f_relationship in further_relationships:
    #             if f_relationship.bundle:
    #                 next_nodes.append(self.graph.nodes[f_relationship.target_node_id])
    #     return next_nodes

    @staticmethod
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

    def get_next_step(self, current_node: BaseNode):
        next_nodes = deque()
        next_relationships = self.get_node_relationships(current_node)
        for relationship in next_relationships:
            if relationship.bundle:
                continue
            node = self.graph.nodes[relationship.target_node_id]
            further_relationships = self.get_node_relationships(node)
            bundled_nodes = deque()
            for f_relationship in further_relationships:
                if f_relationship.bundle:
                    bundled_nodes.append(
                        self.graph.nodes[f_relationship.target_node_id]
                    )
            if bundled_nodes:
                node = self.parse_to_action(node, bundled_nodes)
            next_nodes.append(node)
        return next_nodes

    def acyclic(self):
        check_deque = deque(self.graph.nodes.keys())
        check_dict = {
            key: 0 for key in self.graph.nodes.keys()
        }  # 0: not visited, 1: temp, 2: perm

        def visit(key):
            if check_dict[key] == 2:
                return True
            elif check_dict[key] == 1:
                return False

            check_dict[key] = 1

            out_relationships = self.graph.get_node_relationships(self.graph.nodes[key])
            for node in out_relationships:
                check = visit(node.target_node_id)
                if not check:
                    return False

            check_dict[key] = 2
            return True

        while check_deque:
            key = check_deque.pop()
            check = visit(key)
            if not check:
                return False
        return True

    def send(self, recipient_id: str, category: str, package: Any) -> None:
        mail = BaseMail(
            sender_id=self.id_,
            recipient_id=recipient_id,
            category=category,
            package=package,
        )
        self.pending_outs.append(mail)

    def process(self) -> None:
        for key in list(self.pending_ins.keys()):
            while self.pending_ins[key]:
                mail = self.pending_ins[key].popleft()
                if mail.category == "start":
                    next_nodes = self.get_heads()
                elif mail.category == "end":
                    self.execute_stop = True
                    return
                elif mail.category == "node_id":
                    if mail.package not in self.graph.nodes:
                        raise ValueError(
                            f"Node {mail.package} does not exist in the structure {self.id_}"
                        )
                    next_nodes = self.get_next_step(self.graph.nodes[mail.package])
                elif mail.category == "node" and isinstance(mail.package, BaseNode):
                    if not self.node_exist(mail.package):
                        raise ValueError(
                            f"Node {mail.package} does not exist in the structure {self.id_}"
                        )
                    next_nodes = self.get_next_step(mail.package)
                else:
                    raise ValueError(f"Invalid mail type for structure")

                if not next_nodes:  # tail
                    self.send(
                        recipient_id=mail.sender_id, category="end", package="end"
                    )
                while next_nodes:
                    package = next_nodes.popleft()
                    self.send(
                        recipient_id=mail.sender_id, category="node", package=package
                    )

    async def execute(self, refresh_time=1):
        if not self.acyclic():
            raise ValueError("Structure is not acyclic")

        while not self.execute_stop:
            self.process()
            await AsyncUtil.sleep(refresh_time)

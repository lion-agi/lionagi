"""
This module contains classes for representing and manipulating graph structures.

The module includes the following classes:
- Relationship: Represents a relationship between two nodes in a graph.
- Graph: Represents a graph structure, consisting of nodes and their relationships.
- Structure: Represents a structure that extends the Graph class with additional functionality.

The Structure class adds methods for managing and executing a graph structure, including
adding nodes and relationships, checking conditions, processing incoming and outgoing mails,
and executing the structure.
"""

import time
from typing import List, Any, Dict, Callable
from collections import deque
from pydantic import Field

from lionagi.libs import SysUtil, func_call, AsyncUtil

from .base_node import BaseRelatableNode, BaseNode, Tool
from lionagi.core.mail.schema import BaseMail

from lionagi.core.schema.condition import Condition

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
    condition: Callable = None

    def add_condition(self, condition: Condition):
        """
        Adds a condition to the relationship.

        Args:
            condition (Condition): The condition to add.

        Raises:
            ValueError: If the condition is not an instance of the Condition class.
        """
        if not isinstance(condition, Condition):
            raise ValueError(
                "Invalid condition type, please use Condition class to build a valid condition"
            )
        self.condition = condition

    def check_condition(self, source_obj):
        """
        Checks the condition of the relationship.

        Args:
            source_obj: The source object to evaluate the condition against.

        Returns:
            The result of evaluating the condition.

        Raises:
            ValueError: If the relationship condition function is invalid.
        """
        try:
            return bool(self.condition(source_obj))
        except:
            raise ValueError("Invalid relationship condition function")

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
    Represents a graph structure, consisting of nodes and their relationships.

    Attributes:
        nodes (Dict[str, BaseNode]): A dictionary of nodes in the graph.
        relationships (Dict[str, Relationship]): A dictionary of relationships between nodes in the graph.
        node_relationships (Dict[str, Dict[str, Dict[str, str]]]): A dictionary tracking the relationships of each node.

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
        Retrieves relationships of a specific node or all relationships in the graph.

        Args:
            node (Optional[BaseNode]): The node whose relationships to retrieve. If None, retrieves all relationships.
            out_edge (bool): Whether to retrieve outgoing relationships. If False, retrieves incoming relationships.

        Returns:
            List[Relationship]: A list of relationships.

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

    def get_predecessors(self, node: BaseNode):
        """
        Retrieves the predecessor nodes of a given node.

        Args:
            node (BaseNode): The node whose predecessors to retrieve.

        Returns:
            list: A list of predecessor nodes.
        """
        node_ids = list(self.node_relationships[node.id_]["in"].values())
        nodes = func_call.lcall(node_ids, lambda i: self.nodes[i])
        return nodes

    def get_successors(self, node: BaseNode):
        """
        Retrieves the successor nodes of a given node.

        Args:
            node (BaseNode): The node whose successors to retrieve.

        Returns:
            list: A list of successor nodes.
        """
        node_ids = list(self.node_relationships[node.id_]["out"].values())
        nodes = func_call.lcall(node_ids, lambda i: self.nodes[i])
        return nodes

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
            node_info.update({"class_name": node.__class__.__name__})
            g.add_node(node_id, **node_info)

        for _, relationship in self.relationships.items():
            relationship_info = relationship.to_dict()
            relationship_info.pop("node_id")
            relationship_info.update({"class_name": relationship.__class__.__name__})
            source_node_id = relationship_info.pop("source_node_id")
            target_node_id = relationship_info.pop("target_node_id")
            g.add_edge(source_node_id, target_node_id, **relationship_info)

        return g


class Structure(BaseRelatableNode):
    """
    Represents a structure that extends the Graph class with additional functionality.

    Attributes:
        graph (Graph): The underlying graph structure.
        pending_ins (dict): A dictionary of pending incoming mails.
        pending_outs (deque): A deque of pending outgoing mails.
        execute_stop (bool): A flag indicating whether the execution should stop.
        condition_check_result (bool | None): The result of the last condition check.

    Methods:
        add_node(node: BaseNode) -> None:
            Adds a node to the structure's graph.

        add_relationship(from_node: BaseNode, to_node: BaseNode, bundle=False, condition=None, **kwargs) -> None:
            Adds a relationship between two nodes in the structure's graph.

        get_relationships() -> list[Relationship]:
            Retrieves all relationships in the structure's graph.

        get_node_relationships(node: BaseNode, out_edge=True, labels=None) -> list[Relationship]:
            Retrieves relationships of a specific node in the structure's graph.

        get_predecessors(node: BaseNode) -> list[BaseNode]:
            Retrieves the predecessor nodes of a given node in the structure's graph.

        get_successors(node: BaseNode) -> list[BaseNode]:
            Retrieves the successor nodes of a given node in the structure's graph.

        node_exist(node: BaseNode) -> bool:
            Checks if a node exists in the structure's graph.

        relationship_exist(relationship: Relationship) -> bool:
            Checks if a relationship exists in the structure's graph.

        remove_node(node: BaseNode) -> BaseNode:
            Removes a node from the structure's graph.

        remove_relationship(relationship: Relationship) -> Relationship:
            Removes a relationship from the structure's graph.

        is_empty() -> bool:
            Determines if the structure's graph is empty.

        get_heads() -> list[BaseNode]:
            Retrieves the head nodes of the structure's graph.

        parse_to_action(instruction: BaseNode, bundled_nodes: deque) -> ActionNode:
            Parses an instruction and bundled nodes into an ActionNode.

        async check_condition(relationship: Relationship, executable_id: str) -> bool:
            Checks the condition of a relationship.

        check_condition_structure(relationship: Relationship) -> bool:
            Checks the condition of a relationship within the structure.

        async get_next_step(current_node: BaseNode, executable_id: str) -> list[BaseNode]:
            Retrieves the next step nodes based on the current node and executable ID.

        acyclic() -> bool:
            Checks if the structure's graph is acyclic.

        send(recipient_id: str, category: str, package: Any) -> None:
            Sends a mail to a recipient.

        process_relationship_condition(relationship_id: str) -> None:
            Processes the condition of a relationship.

        async process() -> None:
            Processes the pending incoming mails and performs the corresponding actions.

        async execute(refresh_time=1) -> None:
            Executes the structure by processing incoming mails and updating the execution state.
    """

    graph: Graph = Graph()
    pending_ins: dict = {}
    pending_outs: deque = deque()
    execute_stop: bool = False
    condition_check_result: bool | None = None

    def add_node(self, node: BaseNode | list[BaseNode]):
        """
        Adds a node to the structure's graph.

        Args:
            node (BaseNode): The node to add.
        """
        nodes = [node] if isinstance(node, BaseNode) else node
        for i in nodes:
            self.graph.add_node(i)

    def add_relationship(
        self,
        from_node: BaseNode,
        to_node: BaseNode,
        bundle=False,
        condition=None,
        **kwargs,
    ):
        """
        Adds a relationship between two nodes in the structure's graph.

        Args:
            from_node (BaseNode): The source node of the relationship.
            to_node (BaseNode): The target node of the relationship.
            bundle (bool): Whether the relationship is bundled (default: False).
            condition (Optional[Condition]): The condition for the relationship (default: None).
            **kwargs: Additional keyword arguments for the relationship.

        Raises:
            ValueError: If the source node is a Tool or ActionSelection.
        """
        if isinstance(from_node, Tool) or isinstance(from_node, ActionSelection):
            raise ValueError(
                f"type {type(from_node)} should not be the head of the relationship, "
                f"please switch position and attach it to the tail of the relationship"
            )
        if isinstance(to_node, Tool) or isinstance(to_node, ActionSelection):
            bundle = True
        relationship = Relationship(
            source_node_id=from_node.id_,
            target_node_id=to_node.id_,
            bundle=bundle,
            **kwargs,
        )
        if condition:
            relationship.add_condition(condition)
        self.graph.add_relationship(relationship)

    def get_relationships(self) -> list[Relationship]:
        """
        Retrieves all relationships in the structure's graph.

        Returns:
            list[Relationship]: A list of all relationships.
        """
        return self.graph.get_node_relationships()

    def get_node_relationships(self, node: BaseNode, out_edge=True, labels=None):
        """
        Retrieves relationships of a specific node in the structure's graph.

        Args:
            node (BaseNode): The node whose relationships to retrieve.
            out_edge (bool): Whether to retrieve outgoing relationships (default: True).
            labels (Optional[list]): The labels of the relationships to retrieve (default: None).

        Returns:
            list[Relationship]: A list of relationships for the specified node.
        """
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

    def get_predecessors(self, node: BaseNode):
        """
        Retrieves the predecessor nodes of a given node in the structure's graph.

        Args:
            node (BaseNode): The node whose predecessors to retrieve.

        Returns:
            list[BaseNode]: A list of predecessor nodes.
        """
        return self.graph.get_predecessors(node)

    def get_successors(self, node: BaseNode):
        """
        Retrieves the successor nodes of a given node in the structure's graph.

        Args:
            node (BaseNode): The node whose successors to retrieve.

        Returns:
            list[BaseNode]: A list of successor nodes.
        """
        return self.graph.get_successors(node)

    def node_exist(self, node: BaseNode) -> bool:
        """
        Checks if a node exists in the structure's graph.

        Args:
            node (BaseNode): The node to check.

        Returns:
            bool: True if the node exists, False otherwise.
        """
        return self.graph.node_exist(node)

    def relationship_exist(self, relationship: Relationship) -> bool:
        """
        Checks if a relationship exists in the structure's graph.

        Args:
            relationship (Relationship): The relationship to check.

        Returns:
            bool: True if the relationship exists, False otherwise.
        """
        return self.graph.relationship_exist(relationship)

    def remove_node(self, node: BaseNode) -> BaseNode:
        """
        Removes a node from the structure's graph.

        Args:
            node (BaseNode): The node to remove.

        Returns:
            BaseNode: The removed node.
        """
        return self.graph.remove_node(node)

    def remove_relationship(self, relationship: Relationship) -> Relationship:
        """
        Removes a relationship from the structure's graph.

        Args:
            relationship (Relationship): The relationship to remove.

        Returns:
            Relationship: The removed relationship.
        """
        return self.graph.remove_relationship(relationship)

    def is_empty(self) -> bool:
        """
        Determines if the structure's graph is empty.

        Returns:
            bool: True if the graph has no nodes, False otherwise.
        """
        return self.graph.is_empty()

    def get_heads(self):
        """
        Retrieves the head nodes of the structure's graph.

        Returns:
            list[BaseNode]: A list of head nodes.
        """
        heads = []
        for key in self.graph.node_relationships:
            if not self.graph.node_relationships[key]["in"]:
                heads.append(self.graph.nodes[key])
        return heads

    @staticmethod
    def parse_to_action(instruction: BaseNode, bundled_nodes: deque):
        """
        Parses an instruction and bundled nodes into an ActionNode.

        Args:
            instruction (BaseNode): The instruction node.
            bundled_nodes (deque): A deque of bundled nodes.

        Returns:
            ActionNode: The parsed ActionNode.

        Raises:
            ValueError: If an invalid bundled node is encountered.
        """
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

    async def check_condition(self, relationship, executable_id):
        """
        Checks the condition of a relationship.

        Args:
            relationship (Relationship): The relationship to check the condition for.
            executable_id (str): The ID of the executable.

        Returns:
            bool: True if the condition is met, False otherwise.

        Raises:
            ValueError: If the source type of the condition is invalid.
        """
        if relationship.condition.source_type == "structure":
            return self.check_condition_structure(relationship)
        elif relationship.condition.source_type == "executable":
            self.send(
                recipient_id=executable_id, category="condition", package=relationship
            )
            while self.condition_check_result is None:
                await AsyncUtil.sleep(0.1)
                self.process_relationship_condition(relationship.id_)
                continue
            check_result = self.condition_check_result
            self.condition_check_result = None
            return check_result
        else:
            raise ValueError("Invalid source_type.")

    def check_condition_structure(self, relationship):
        """
        Checks the condition of a relationship within the structure.

        Args:
            relationship (Relationship): The relationship to check the condition for.

        Returns:
            bool: The result of the condition check.
        """
        return relationship.condition(self)

    async def get_next_step(self, current_node: BaseNode, executable_id):
        """
        Retrieves the next step nodes based on the current node and executable ID.

        Args:
            current_node (BaseNode): The current node.
            executable_id (str): The ID of the executable.

        Returns:
            list[BaseNode]: A list of next step nodes.
        """
        next_nodes = []
        next_relationships = self.get_node_relationships(current_node)
        for relationship in next_relationships:
            if relationship.bundle:
                continue
            if relationship.condition:
                check = await self.check_condition(relationship, executable_id)
                if not check:
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
        """
        Checks if the structure's graph is acyclic.

        Returns:
            bool: True if the graph is acyclic, False otherwise.
        """
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
        """
        Sends a mail to a recipient.

        Args:
            recipient_id (str): The ID of the recipient.
            category (str): The category of the mail.
            package (Any): The package to send.
        """
        mail = BaseMail(
            sender_id=self.id_,
            recipient_id=recipient_id,
            category=category,
            package=package,
        )
        self.pending_outs.append(mail)

    def process_relationship_condition(self, relationship_id):
        """
        Processes the condition of a relationship.

        Args:
            relationship_id (str): The ID of the relationship to process the condition for.
        """
        for key in list(self.pending_ins.keys()):
            skipped_requests = deque()
            while self.pending_ins[key]:
                mail = self.pending_ins[key].popleft()
                if (
                    mail.category == "condition"
                    and mail.package["relationship_id"] == relationship_id
                ):
                    self.condition_check_result = mail.package["check_result"]
                else:
                    skipped_requests.append(mail)
            self.pending_ins[key] = skipped_requests

    async def process(self) -> None:
        """
        Processes the pending incoming mails and performs the corresponding actions.
        """
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
                    next_nodes = await self.get_next_step(
                        self.graph.nodes[mail.package], mail.sender_id
                    )
                elif mail.category == "node" and isinstance(mail.package, BaseNode):
                    if not self.node_exist(mail.package):
                        raise ValueError(
                            f"Node {mail.package} does not exist in the structure {self.id_}"
                        )
                    next_nodes = await self.get_next_step(mail.package, mail.sender_id)
                else:
                    raise ValueError(f"Invalid mail type for structure")

                if not next_nodes:  # tail
                    self.send(
                        recipient_id=mail.sender_id, category="end", package="end"
                    )
                else:
                    if len(next_nodes) == 1:
                        self.send(
                            recipient_id=mail.sender_id,
                            category="node",
                            package=next_nodes[0],
                        )
                    else:
                        self.send(
                            recipient_id=mail.sender_id,
                            category="node_list",
                            package=next_nodes,
                        )

    async def execute(self, refresh_time=1):
        """
        Executes the structure by processing incoming mails and updating the execution state.

        Args:
            refresh_time (int): The refresh time for execution (default: 1).

        Raises:
            ValueError: If the structure's graph is not acyclic.
        """
        if not self.acyclic():
            raise ValueError("Structure is not acyclic")

        while not self.execute_stop:
            await self.process()
            await AsyncUtil.sleep(refresh_time)

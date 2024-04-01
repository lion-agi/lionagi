from typing import Any
from collections import deque
from lionagi.libs import AsyncUtil

from ..schema import BaseNode, ActionNode, ActionSelection
from ..mail import BaseMail
from ..tool import Tool
from ..relations import Relationship
from .graph import Graph
from .base_structure import BaseStructure


class Structure(BaseStructure):
    """
    A class representing a structure of nodes with relationships.

    Attributes:
        graph (Graph): The graph representing the structure.
        pending_ins (dict): A dictionary of pending incoming mails.
        pending_outs (deque): A deque of pending outgoing mails.
        execute_stop (bool): A flag indicating whether to stop execution.
        condition_check_result (bool | None): The result of a condition check.
    """

    graph: Graph = Graph()
    pending_ins: dict = {}
    pending_outs: deque = deque()
    execute_stop: bool = False
    condition_check_result: bool | None = None

    def add_node(self, node: BaseNode | list[BaseNode]):
        """
        Add a node or a list of nodes to the structure's graph.

        Args:
            node (BaseNode | list[BaseNode]): The node or list of nodes to add.
        """
        nodes = [node] if isinstance(node, BaseNode) else node
        for i in nodes:
            self.graph.add_node(i)

    @property
    def relationships(self):
        """
        Get the relationships in the structure's graph.

        Returns:
            dict: The relationships in the graph.
        """
        return self.graph.relationships

    def add_relationship(
        self,
        from_node: BaseNode,
        to_node: BaseNode,
        bundle=False,
        condition=None,
        **kwargs,
    ):
        """
        Add a relationship between two nodes in the structure's graph.

        Args:
            from_node (BaseNode): The source node of the relationship.
            to_node (BaseNode): The target node of the relationship.
            bundle (bool, optional): Whether the relationship is bundled. Defaults to False.
            condition (Any, optional): The condition for the relationship. Defaults to None.
            **kwargs: Additional keyword arguments for the relationship.

        Raises:
            ValueError: If the source node is of type Tool or ActionSelection.
        """
        if isinstance(from_node, Tool) or isinstance(from_node, ActionSelection):
            raise ValueError(
                f"type {type(from_node)} should not be the head of the relationship, "
                f"please switch position and attach it to the tail of the relationship"
            )
        if isinstance(to_node, Tool) or isinstance(to_node, ActionSelection):
            bundle = True

        relationship = self._build_relationship(
            from_node, to_node, bundle=bundle, condition=condition, **kwargs
        )

        self.graph.add_relationship(relationship)

    def get_node_relationships(self, node: BaseNode, out_edge=True, labels=None):
        """
        Get the relationships of a node in the structure's graph.

        Args:
            node (BaseNode): The node to get relationships for.
            out_edge (bool, optional): Whether to get outgoing relationships. Defaults to True.
            labels (Any, optional): The labels to filter the relationships. Defaults to None.

        Returns:
            list[Relationship]: The relationships of the node.
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
        Get the predecessor nodes of a node in the structure's graph.

        Args:
            node (BaseNode): The node to get predecessors for.

        Returns:
            list[BaseNode]: The predecessor nodes of the node.
        """
        return self.graph.get_node_predecessors(node)

    def get_successors(self, node: BaseNode):
        """
        Get the successor nodes of a node in the structure's graph.

        Args:
            node (BaseNode): The node to get successors for.

        Returns:
            list[BaseNode]: The successor nodes of the node.
        """
        return self.graph.get_node_successors(node)

    def has_node(self, node: BaseNode | str | list) -> bool:
        """
        Check if a node exists in the structure's graph.

        Args:
            node (BaseNode): The node to check.

        Returns:
            bool: True if the node exists, False otherwise.
        """
        return self.graph.has_node(node)

    def has_relationship(self, relationship: Relationship | str) -> bool:
        """
        Check if a relationship exists in the structure's graph.

        Args:
            relationship (Relationship): The relationship to check.

        Returns:
            bool: True if the relationship exists, False otherwise.
        """

        return self.graph.has_relationship(relationship)

    def remove_node(self, node: BaseNode | str | list) -> BaseNode:
        """
        Remove a node from the structure's graph.

        Args:
            node (BaseNode): The node to remove.

        Returns:
            BaseNode: The removed node.
        """
        return self.graph.remove_node(node)

    def remove_relationship(self, relationship: Relationship) -> Relationship:
        """
        Remove a relationship from the structure's graph.

        Args:
            relationship (Relationship): The relationship to remove.

        Returns:
            Relationship: The removed relationship.
        """
        return self.graph.remove_relationship(relationship)

    @property
    def is_empty(self) -> bool:
        """
        Check if the structure's graph is empty.

        Returns:
            bool: True if the graph is empty, False otherwise.
        """

        return self.graph.is_empty

    def get_heads(self):
        """
        Get the head nodes (nodes with no incoming relationships) in the structure's graph.

        Returns:
            list[BaseNode]: The head nodes.
        """
        heads = []
        for key in self.graph.node_relationships:
            if not self.graph.node_relationships[key]["in"]:
                heads.append(self.graph.nodes[key])
        return heads

    @staticmethod
    def parse_to_action(instruction: BaseNode, bundled_nodes: deque):
        """
        Parse an instruction node and bundled nodes into an ActionNode.

        Args:
            instruction (BaseNode): The instruction node.
            bundled_nodes (deque): The bundled nodes.

        Returns:
            ActionNode: The parsed ActionNode.

        Raises:
            ValueError: If any of the bundled nodes are invalid.
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

    async def check_condition(self, relationship: Relationship, executable_id):
        """
        Check the condition of a relationship.

        Args:
            relationship (Relationship): The relationship to check the condition for.
            executable_id (str): The ID of the executable.

        Returns:
            bool: The result of the condition check.

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

    def check_condition_structure(self, relationship: Relationship):
        """
        Check the condition of a relationship within the structure.

        Args:
            relationship (Relationship): The relationship to check the condition for.

        Returns:
            bool: The result of the condition check.
        """
        return relationship.condition(self)

    async def get_next_step(self, current_node: BaseNode, executable_id):
        """
        Get the next step nodes based on the current node.

        Args:
            current_node (BaseNode): The current node.
            executable_id (str): The ID of the executable.

        Returns:
            list[BaseNode]: The next step nodes.
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
        Check if the structure's graph is acyclic.

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

            out_relationships = self.graph.get_node_relationships(
                self.graph.nodes[key], out_edge=True
            )
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
        Send a mail to a recipient.

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
        Process the condition of a relationship.

        Args:
            relationship_id (str): The ID of the relationship.
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
        Process the pending incoming mails and perform the corresponding actions.
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
                    if not self.has_node(mail.package):
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
        Execute the structure.

        Args:
            refresh_time (int, optional): The refresh time in seconds. Defaults to 1.

        Raises:
            ValueError: If the structure's graph is not acyclic.
        """
        if not self.acyclic():
            raise ValueError("Structure is not acyclic")

        while not self.execute_stop:
            await self.process()
            await AsyncUtil.sleep(refresh_time)

    @staticmethod
    def _build_relationship(
        from_node: BaseNode, to_node: BaseNode, condition=None, **kwargs
    ):
        """
        Build a relationship between two nodes.

        Args:
            from_node (BaseNode): The source node of the relationship.
            to_node (BaseNode): The target node of the relationship.
            condition (Any, optional): The condition for the relationship. Defaults to None.
            **kwargs: Additional keyword arguments for the relationship.

        Returns:
            Relationship: The built relationship.
        """
        relationship = Relationship(
            source_node_id=from_node.id_, target_node_id=to_node.id_, **kwargs
        )
        if condition:
            relationship.add_condition(condition)
        return relationship

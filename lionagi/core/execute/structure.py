from typing import Any
from collections import deque

from lionagi.libs import AsyncUtil
from lionagi.core.schema import Edge

from lionagi.core.schema.base_node import BaseNode, BaseNode
from lionagi.core.mail.schema import BaseMail

from lionagi.core.schema.action_node import ActionNode, ActionSelection
from lionagi.core.tool.tool import Tool
from lionagi.core.structure.graph import Graph


class Structure(BaseNode):

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
        relationship = Edge(
            source_node_id=from_node.id_,
            target_node_id=to_node.id_,
            bundle=bundle,
            **kwargs,
        )
        if condition:
            relationship.add_condition(condition)
        self.graph.add_relationship(relationship)

    def get_relationships(self) -> list[Edge]:
        """
        Retrieves all relationships in the structure's graph.

        Returns:
            list[Edge]: A list of all relationships.
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
            list[Edge]: A list of relationships for the specified node.
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

    def relationship_exist(self, relationship: Edge) -> bool:
        """
        Checks if a relationship exists in the structure's graph.

        Args:
            relationship (Edge): The relationship to check.

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

    def remove_relationship(self, relationship: Edge) -> Edge:
        """
        Removes a relationship from the structure's graph.

        Args:
            relationship (Edge): The relationship to remove.

        Returns:
            Edge: The removed relationship.
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

    async def check_condition(self, relationship, executable_id, request_source):
        """
        Checks the condition of a relationship.

        Args:
            relationship (Edge): The relationship to check the condition for.
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
                recipient_id=executable_id, category="condition", package={"request_source": request_source, "package": relationship}
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
            relationship (Edge): The relationship to check the condition for.

        Returns:
            bool: The result of the condition check.
        """
        return relationship.condition(self)

    async def get_next_step(self, current_node: BaseNode, executable_id, request_source):
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
                check = await self.check_condition(relationship, executable_id, request_source)
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
                    and mail.package["package"]["relationship_id"] == relationship_id
                ):
                    self.condition_check_result = mail.package["package"]["check_result"]
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
                    if mail.package["package"] not in self.graph.nodes:
                        raise ValueError(
                            f"Node {mail.package} does not exist in the structure {self.id_}"
                        )
                    next_nodes = await self.get_next_step(
                        self.graph.nodes[mail.package["package"]], mail.sender_id, mail.package["request_source"]
                    )
                elif mail.category == "node" and isinstance(mail.package["package"], BaseNode):
                    if not self.node_exist(mail.package["package"]):
                        raise ValueError(
                            f"Node {mail.package} does not exist in the structure {self.id_}"
                        )
                    next_nodes = await self.get_next_step(mail.package["package"], mail.sender_id, mail.package["request_source"])
                else:
                    raise ValueError(f"Invalid mail type for structure")

                if not next_nodes:  # tail
                    self.send(
                        recipient_id=mail.sender_id,
                        category="end",
                        package={"request_source": mail.package["request_source"], "package": "end"}
                    )
                else:
                    if len(next_nodes) == 1:
                        self.send(
                            recipient_id=mail.sender_id,
                            category="node",
                            package={"request_source": mail.package["request_source"], "package": next_nodes[0]}
                        )
                    else:
                        self.send(
                            recipient_id=mail.sender_id,
                            category="node_list",
                            package={"request_source": mail.package["request_source"], "package": next_nodes}
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

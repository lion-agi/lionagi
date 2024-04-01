from typing import Any, overload
from collections import deque
from pydantic import Field
from lionagi.libs import AsyncUtil

from ..schema import BaseNode, ActionSelection, Edge
from ..mail import BaseMail
from ..tool import Tool

from ..structure.base_structure import BaseStructure
from ..structure.graph import Graph
from .utils import parse_to_action


class ExecutableStructure(BaseStructure):

    internal: BaseStructure = Field(
        Graph(), description="Internal structure of the structure"
    )
    pending_ins: dict = {}
    pending_outs: deque = deque()
    execute_stop: bool = False
    condition_check_result: bool | None = None

    def add_node(self, node: list | BaseNode):
        self.internal.add_structure_node(node)

    @property
    def internal_nodes(self):
        return self.internal.structure_nodes

    @property
    def internal_edges(self):
        return self.internal.structure_edges

    @property
    def internal_node_edges(self):
        return self.internal.node_edges

    @property
    def internal_is_empty(self) -> bool:
        return self.internal.is_empty

    def add_edge(
        self,
        from_node: BaseNode,
        to_node: BaseNode,
        bundle=False,
        condition=None,
        **kwargs,
    ):
        if isinstance(from_node, Tool) or isinstance(from_node, ActionSelection):
            raise ValueError(
                f"type {type(from_node)} should not be the head of the edge, "
                f"please switch position and attach it to the tail of the edge"
            )
        if isinstance(to_node, Tool) or isinstance(to_node, ActionSelection):
            bundle = True

        edge = self._build_edge(
            from_node, to_node, bundle=bundle, condition=condition, **kwargs
        )

        self.internal.add_structure_edge(edge)

    def get_internal_node_edges(self, node: BaseNode, direction="out", labels=None):
        edges = self.internal.get_node_edges(node, direction)
        if labels:
            if not isinstance(labels, list):
                labels = [labels]
            result = []
            for e in edges:
                if e.label in labels:
                    result.append(e)
            edges = result
        return edges

    def get_internal_node_predecessors(self, node: BaseNode):
        return self.internal.get_node_predecessors(node)

    def get_internal_node_successors(self, node: BaseNode):
        return self.internal.get_node_successors(node)

    def has_internal_node(self, node: BaseNode | str | list) -> bool:
        return self.internal.has_structure_node(node)

    def has_internal_edge(self, edge: Edge | str) -> bool:
        return self.internal.has_structure_edge(edge)

    def remove_node(self, node: BaseNode | str | list) -> BaseNode:
        return self.internal.remove_structure_node(node)

    def remove_edge(self, edge: Edge | str) -> bool:
        try:
            a = self.internal.remove_structure_edge(edge)
            if a:
                return True
        except Exception as e:
            raise ValueError(f"Error removing edge: {e}")

    def get_heads(self):
        return [
            self.internal_nodes[key]
            for key in self.internal_node_edges
            if not self.internal_node_edges[key]["in"]
        ]

    async def check_edge_condition(self, edge: Edge, executable_id):
        if edge.condition.source_type == "structure":
            return self._check_structure_condition(edge)

        elif edge.condition.source_type == "executable":
            return await self._check_executable_condition(edge, executable_id)

        else:
            raise ValueError("Invalid source_type.")

    def acyclic(self):
        """
        Check if the structure's graph is acyclic.

        Returns:
            bool: True if the graph is acyclic, False otherwise.
        """
        check_deque = deque(self.internal_nodes.keys())
        check_dict = {
            key: 0 for key in self.internal_nodes.keys()
        }  # 0: not visited, 1: temp, 2: perm

        def visit(key):
            if check_dict[key] == 2:
                return True
            elif check_dict[key] == 1:
                return False

            check_dict[key] = 1

            out_edges = self.get_internal_node_edges(self.internal_nodes[key])

            for node in out_edges:
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

    def process_edge_condition(self, edge_id):
        """
        Process the condition of a edge.

        Args:
            edge_id (str): The ID of the edge.
        """
        for key in list(self.pending_ins.keys()):
            skipped_requests = deque()
            while self.pending_ins[key]:
                mail = self.pending_ins[key].popleft()
                if mail.category == "condition" and mail.package["edge_id"] == edge_id:
                    self.condition_check_result = mail.package["check_result"]
                else:
                    skipped_requests.append(mail)
            self.pending_ins[key] = skipped_requests

    async def forward(self) -> None:
        """
        Process the pending incoming mails and perform the corresponding actions.
        """
        for key in list(self.pending_ins.keys()):
            while self.pending_ins[key]:
                mail = self.pending_ins[key].popleft()
                try:
                    next_nodes = await self._handle_mail(mail)
                except Exception as e:
                    raise ValueError(f"Error handling mail: {e}") from e
                if next_nodes:
                    self._send_mail(next_nodes, mail)
                else:
                    return

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
            await self.forward()
            await AsyncUtil.sleep(refresh_time)

    @staticmethod
    def _build_edge(from_node: BaseNode, to_node: BaseNode, condition=None, **kwargs):
        edge = Edge(source_node_id=from_node.id_, target_node_id=to_node.id_, **kwargs)
        if condition:
            edge.add_condition(condition)
        return edge

    def _check_structure_condition(self, edge: Edge):
        """
        Check the condition of a edge within the structure.

        Args:
            relationship (Relationship): The edge to check the condition for.

        Returns:
            bool: The result of the condition check.
        """
        return edge.condition(self)

    async def _check_executable_condition(self, edge: Edge, executable_id):
        self.send(recipient_id=executable_id, category="condition", package=edge)
        while self.condition_check_result is None:
            await AsyncUtil.sleep(0.1)
            self.process_edge_condition(edge.id_)
            continue
        check_result = self.condition_check_result
        self.condition_check_result = None
        return check_result

    async def _next_step(self, current_node: BaseNode, executable_id):
        """
        Get the next step nodes based on the current node.

        Args:
            current_node (BaseNode): The current node.
            executable_id (str): The ID of the executable.

        Returns:
            list[BaseNode]: The next step nodes.
        """
        next_nodes = []
        next_relationships = self.get_node_edges(current_node)
        for relationship in next_relationships:
            if relationship.bundle:
                continue
            if relationship.condition:
                check = await self.check_edge_condition(relationship, executable_id)
                if not check:
                    continue
            node = self.internal_nodes[relationship.target_node_id]
            further_relationships = self.get_node_edges(node)
            bundled_nodes = deque()
            for f_relationship in further_relationships:
                if f_relationship.bundle:
                    bundled_nodes.append(
                        self.internal_nodes[f_relationship.target_node_id]
                    )
            if bundled_nodes:
                node = parse_to_action(node, bundled_nodes)
            next_nodes.append(node)
        return next_nodes

    async def _handle_node_id(self, mail):
        if mail.package not in self.internal_nodes:
            raise ValueError(
                f"Node {mail.package} does not exist in the structure {self.id_}"
            )
        return await self._next_step(self.internal_nodes[mail.package], mail.sender_id)

    async def _handle_node(self, mail):
        if not self.has_structure_node(mail.package):
            raise ValueError(
                f"Node {mail.package} does not exist in the structure {self.id_}"
            )
        return await self._next_step(mail.package, mail.sender_id)

    async def _handle_mail(self, mail):

        if mail.category == "start":
            return self.get_heads()

        elif mail.category == "end":
            self.execute_stop = True
            return None

        elif mail.category == "node_id":
            try:
                return await self._handle_node_id(mail)
            except Exception as e:
                raise ValueError(f"Error handling node id: {e}") from e

        elif mail.category == "node" and isinstance(mail.package, BaseNode):
            try:
                return await self._handle_node(mail)
            except Exception as e:
                raise ValueError(f"Error handling node: {e}") from e

        else:
            raise ValueError(f"Invalid mail type for structure")

    def _send_mail(self, next_nodes, mail):
        if not next_nodes:  # tail
            self.send(recipient_id=mail.sender_id, category="end", package="end")
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

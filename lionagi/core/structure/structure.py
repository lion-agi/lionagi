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

    @property
    def relationships(self):
        return self.graph.relationships

    def add_relationship(
        self,
        from_node: BaseNode,
        to_node: BaseNode,
        bundle=False,
        condition=None,
        **kwargs,
    ):
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
        return self.graph.get_node_predecessors(node)

    def get_successors(self, node: BaseNode):
        return self.graph.get_node_successors(node)

    def has_node(self, node: BaseNode) -> bool:
        return self.graph.has_node(node)

    def has_relationship(self, relationship: Relationship) -> bool:
        return self.graph.has_relationship(relationship)

    def remove_node(self, node: BaseNode) -> BaseNode:
        return self.graph.remove_node(node)

    def remove_relationship(self, relationship: Relationship) -> Relationship:
        return self.graph.remove_relationship(relationship)

    def is_empty(self) -> bool:
        return self.graph.is_empty()

    def get_heads(self):
        heads = []
        for key in self.graph.node_relationships:
            if not self.graph.node_relationships[key]["in"]:
                heads.append(self.graph.nodes[key])
        return heads

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

    async def check_condition(self, relationship: Relationship, executable_id):
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
        return relationship.condition(self)

    async def get_next_step(self, current_node: BaseNode, executable_id):
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
        mail = BaseMail(
            sender_id=self.id_,
            recipient_id=recipient_id,
            category=category,
            package=package,
        )
        self.pending_outs.append(mail)

    def process_relationship_condition(self, relationship_id):
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
        if not self.acyclic():
            raise ValueError("Structure is not acyclic")

        while not self.execute_stop:
            await self.process()
            await AsyncUtil.sleep(refresh_time)

    @staticmethod
    def _build_relationship(
        from_node: BaseNode, to_node: BaseNode, condition=None, **kwargs
    ):
        relationship = Relationship(
            source_node_id=from_node.id_, target_node_id=to_node.id_, **kwargs
        )
        if condition:
            relationship.add_condition(condition)
        return relationship

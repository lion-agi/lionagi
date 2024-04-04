from abc import ABC
from collections import deque

from lionagi.libs import AsyncUtil

from lionagi.core.schema import BaseNode, ActionNode, ActionSelection, Edge
from lionagi.core.tool import Tool
from lionagi.core.mail import BaseMail
from lionagi.core.execute.base_executor import BaseExecutor


class MailExecutor(BaseExecutor, ABC):
    condition_check_result: bool | None = None

    async def check_edge_condition(self, edge: Edge, executable_id, request_source):
        if edge.condition.source_type == "structure":
            return edge.condition(self)

        elif edge.condition.source_type == "executable":
            return await self._check_executable_condition(edge, executable_id, request_source)

        else:
            raise ValueError("Invalid source_type.")
        
    def _process_edge_condition(self, edge_id):
        """
        Process the condition of a edge.

        Args:
            edge_id (str): The ID of the edge.
        """
        for key in list(self.pending_ins.keys()):
            skipped_requests = deque()
            while self.pending_ins[key]:
                mail: BaseMail = self.pending_ins[key].popleft()
                if (
                    mail.category == "condition"
                    and mail.package["package"]["edge_id"] == edge_id
                ):
                    self.condition_check_result = mail.package["package"]["check_result"]
                else:
                    skipped_requests.append(mail)
            self.pending_ins[key] = skipped_requests

    async def _check_executable_condition(self, edge: Edge, executable_id, request_source):
        self.send(
            recipient_id=executable_id, category="condition", package={"request_source": request_source, "package": edge}
        )
        while self.condition_check_result is None:
            await AsyncUtil.sleep(0.1)
            self._process_edge_condition(edge.id_)
            continue
        check_result = self.condition_check_result
        self.condition_check_result = None
        return check_result
    

    async def _handle_node_id(self, mail: BaseMail):
        if mail.package["package"] not in self.structure_nodes:
            raise ValueError(
                f"Node {mail.package} does not exist in the structure {self.id_}"
            )
        return await self._next_node(
            self.structure_nodes[mail.package["package"]], mail.sender_id, mail.package["request_source"]
        )

    async def _handle_node(self, mail: BaseMail):
        if not self.node_exist(mail.package["package"]):
            raise ValueError(
                f"Node {mail.package} does not exist in the structure {self.id_}"
            )
        return await self._next_node(mail.package["package"], mail.sender_id, mail.package["request_source"])

    async def _handle_mail(self, mail: BaseMail):

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

        elif mail.category == "node" and isinstance(mail.package["package"], BaseNode):
            try:
                return await self._handle_node(mail)
            except Exception as e:
                raise ValueError(f"Error handling node: {e}") from e

        else:
            raise ValueError(f"Invalid mail type for structure")

    async def _next_node(self, current_node: BaseNode, executable_id, request_source):
        """
        Get the next step nodes based on the current node.

        Args:
            current_node (BaseNode): The current node.
            executable_id (str): The ID of the executable.

        Returns:
            list[BaseNode]: The next step nodes.
        """
        next_nodes = []
        next_edges = self.get_node_edges(current_node)
        for edge in next_edges:
            if edge.bundle:
                continue
            if edge.condition:
                check = await self.check_edge_condition(edge, executable_id, request_source)
                if not check:
                    continue
            node = self.structure_nodes[edge.target_node_id]
            further_edges = self.get_node_edges(node)
            bundled_nodes = deque()
            for f_edge in further_edges:
                if f_edge.bundle:
                    bundled_nodes.append(
                        self.structure_nodes[f_edge.target_node_id]
                    )
            if bundled_nodes:
                node = self.parse_bundled_to_action(node, bundled_nodes)
            next_nodes.append(node)
        return next_nodes

    def _send_mail(self, next_nodes: list | None, mail: BaseMail):
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

    @staticmethod
    def parse_bundled_to_action(instruction: BaseNode, bundled_nodes: deque):
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

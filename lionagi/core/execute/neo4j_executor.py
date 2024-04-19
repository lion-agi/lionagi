from collections import deque
import json
from typing import Callable

from lionagi.core.execute.base_executor import BaseExecutor
from lionagi.integrations.storage.neo4j import Neo4j
from lionagi.integrations.storage.storage_util import ParseNode
from lionagi.core.generic import ActionNode
from lionagi.core.agent.base_agent import BaseAgent
from lionagi.core.execute.instruction_map_executor import InstructionMapExecutor

from lionagi.core.mail.schema import BaseMail
from lionagi.core.tool import Tool
from lionagi.core.generic import ActionSelection, Edge

from lionagi.libs import AsyncUtil


class Neo4jExecutor(BaseExecutor):
    driver: Neo4j | None
    structure_id: str = None
    structure_name: str = None
    middle_agents: list | None = None
    default_agent_executable: BaseExecutor = InstructionMapExecutor()
    condition_check_result: bool | None = None

    async def check_edge_condition(self, condition, executable_id, request_source, head, tail):
        if condition.source_type == "structure":
            return condition(self)
        elif condition.source_type == "executable":
            return await self._check_executable_condition(condition, executable_id, head, tail, request_source)

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
                    self.condition_check_result = mail.package["package"][
                        "check_result"
                    ]
                else:
                    skipped_requests.append(mail)
            self.pending_ins[key] = skipped_requests

    async def _check_executable_condition(self, condition, executable_id, head, tail, request_source):
        edge = Edge(head=head, tail=tail, condition=condition)
        self.send(
            recipient_id=executable_id,
            category="condition",
            package={"request_source": request_source, "package": edge},
        )
        while self.condition_check_result is None:
            await AsyncUtil.sleep(0.1)
            self._process_edge_condition(edge.id_)
            continue
        check_result = self.condition_check_result
        self.condition_check_result = None
        return check_result

    @staticmethod
    def parse_bundled_to_action(instruction, bundle_list):
        bundled_nodes = deque()
        for node_labels, node_properties in bundle_list:
            try:
                if "ActionSelection" in node_labels:
                    node = ParseNode.parse_actionSelection(node_properties)
                    bundled_nodes.append(node)
                elif "Tool" in node_labels:
                    node = ParseNode.parse_tool(node_properties)
                    bundled_nodes.append(node)
                else:
                    raise ValueError(
                        f"Invalid bundle node {node_properties.id}. Valid nodes are ActionSelection or Tool")
            except Exception as e:
                raise ValueError(f"Failed to parse ActionSelection or Tool node {node_properties.id}. Error: {e}")

        action_node = ActionNode(instruction=instruction)
        while bundled_nodes:
            node = bundled_nodes.popleft()
            if isinstance(node, ActionSelection):
                action_node.action = node.action
                action_node.action_kwargs = node.action_kwargs
            elif isinstance(node, Tool):
                action_node.tools.append(node)
        return action_node

    def parse_agent(self, node_properties):
        output_parser = ParseNode.convert_to_def(node_properties["outputParser"])

        structure = Neo4jExecutor(driver=self.driver, structure_id=node_properties["structureId"])
        agent = BaseAgent(structure=structure, executable=self.default_agent_executable, output_parser=output_parser)
        agent.id_ = node_properties["id"]
        agent.timestamp = node_properties["timestamp"]
        return agent

    async def _next_node(self, query_list, node_id=None, executable_id=None, request_source=None):
        next_nodes = []
        for edge_properties, node_labels, node_properties in query_list:
            if 'condition' in edge_properties.keys():
                try:
                    condition = json.loads(edge_properties['condition'])
                    condition_cls = await self.driver.get_condition_cls_code(condition['class'])
                    condition_obj = ParseNode.parse_condition(condition, condition_cls)

                    head = node_id
                    tail = node_properties['id']
                    check = await self.check_edge_condition(condition_obj, executable_id, request_source, head, tail)
                    if not check:
                        continue
                except Exception as e:
                    raise ValueError(
                        f"Failed to use condition {edge_properties['condition']} from {node_id} to {node_properties['id']}, Error: {e}")

            try:
                if "System" in node_labels:
                    node = ParseNode.parse_system(node_properties)
                elif "Instruction" in node_labels:
                    node = ParseNode.parse_instruction(node_properties)
                elif "Agent" in node_labels:
                    node = self.parse_agent(node_properties)

                else:
                    raise ValueError(f"Invalid start node {node_properties.id}. Valid nodes are System or Instruction")
            except Exception as e:
                raise ValueError(f"Failed to parse System or Instruction node {node_properties.id}. Error: {e}")

            bundle_list = await self.driver.get_bundle(node.id_)

            if bundle_list and "System" in node_labels:
                raise ValueError("System node does not support bundle edge")
            if bundle_list:
                node = self.parse_bundled_to_action(node, bundle_list)
            next_nodes.append(node)
        return next_nodes

    async def _handle_start(self):
        try:
            id, head_list = await self.driver.get_heads(self.structure_name, self.structure_id)
            self.structure_id = id
            return await self._next_node(head_list)
        except Exception as e:
            raise ValueError(f"Error in searching for structure in Neo4j. Error: {e}")

    async def _handle_node_id(self, node_id, executable_id, request_source):
        check = await self.driver.node_exist(node_id)
        if not check:
            raise ValueError(f"Node {node_id} if not found in the database")
        node_list = await self.driver.get_forwards(node_id)
        return await self._next_node(node_list, node_id, executable_id, request_source)

    async def _handle_mail(self, mail: BaseMail):
        if mail.category == "start":
            try:
                return await self._handle_start()
            except Exception as e:
                raise ValueError(f"Error in start. Error: {e}")

        elif mail.category == "end":
            self.execute_stop = True
            return None

        elif mail.category == "node_id":
            try:
                node_id = mail.package["package"]
                executable_id = mail.sender_id
                request_source = mail.package["request_source"]
                return await self._handle_node_id(node_id, executable_id, request_source)
            except Exception as e:
                raise ValueError(f"Error in handling node_id: {e}")
        elif mail.category == "node":
            try:
                node_id = mail.package["package"].id_
                executable_id = mail.sender_id
                request_source = mail.package["request_source"]
                return await self._handle_node_id(node_id, executable_id, request_source)
            except Exception as e:
                raise ValueError(f"Error in handling node: {e}")
        else:
            raise ValueError(f"Invalid mail type for structure")

    def _send_mail(self, next_nodes: list | None, mail: BaseMail):
        if not next_nodes:  # tail
            self.send(
                recipient_id=mail.sender_id,
                category="end",
                package={
                    "request_source": mail.package["request_source"],
                    "package": "end",
                },
            )
        else:
            if len(next_nodes) == 1:
                self.send(
                    recipient_id=mail.sender_id,
                    category="node",
                    package={
                        "request_source": mail.package["request_source"],
                        "package": next_nodes[0],
                    },
                )
            else:
                self.send(
                    recipient_id=mail.sender_id,
                    category="node_list",
                    package={
                        "request_source": mail.package["request_source"],
                        "package": next_nodes,
                    },
                )

    async def forward(self) -> None:
        for key in list(self.pending_ins.keys()):
            while self.pending_ins[key]:
                mail: BaseMail = self.pending_ins[key].popleft()
                try:
                    if mail == "end":
                        self.execute_stop = True
                        return
                    next_nodes = await self._handle_mail(mail)
                    self._send_mail(next_nodes, mail)
                except Exception as e:
                    raise ValueError(f"Error handling mail: {e}") from e

    async def execute(self, refresh_time=1):
        while not self.execute_stop:
            await self.forward()
            await AsyncUtil.sleep(refresh_time)
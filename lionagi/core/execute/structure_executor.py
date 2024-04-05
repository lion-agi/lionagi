from typing import overload

from lionagi.libs import AsyncUtil
from lionagi.core.schema import BaseNode, ActionSelection, Edge
from lionagi.core.tool import Tool

from lionagi.core.structure.graph import Graph
from lionagi.core.execute.mail_executor import MailExecutor


class StructureExecutor(Graph, MailExecutor):
    
    def add_node(self, node: list | BaseNode):
        self.add_structure_node(node)

    def remove_node(self, node: BaseNode | str | list) -> BaseNode:
        return self.remove_structure_node(node)
    
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

        self.add_structure_edge(edge)

    def remove_edge(self, edge: Edge | str) -> bool:
        try:
            a = self.remove_structure_edge(edge)
            if a:
                return True
        except Exception as e:
            raise ValueError(f"Error removing edge: {e}")
        
    async def forward(self) -> None:
        """
        Process the pending incoming mails and perform the corresponding actions.
        """
        for key in list(self.pending_ins.keys()):
            while self.pending_ins[key]:
                mail = self.pending_ins[key].popleft()
                try:
                    if mail.category == "end":
                        self.execute_stop = True
                        return
                    next_nodes = await self._handle_mail(mail)
                except Exception as e:
                    raise ValueError(f"Error handling mail: {e}") from e
                self._send_mail(next_nodes, mail)

    async def execute(self, refresh_time=1):
        if not self.acyclic():
            raise ValueError("Structure is not acyclic")

        while not self.execute_stop:
            await self.forward()
            await AsyncUtil.sleep(refresh_time)
            

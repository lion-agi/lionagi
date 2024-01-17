from lionagi.structures import Relationship, Structure
from ..messages import Instruction
from lionagi.schema import Tool
from typing import List, Union

# dynamically structured preconfigured instructions

class InstructionSet(Structure):
    last_instruct: str = None
    first_instruct: str = None
    instruct_len: int = 0

    def push_instruction(self, instruction: Instruction, tools: Union[Tool, List[Tool]] = None):
        if self.graph.is_empty():
            self.graph.add_node(instruction)
            self.last_instruct = instruction.id_
            self.first_instruct = instruction.id_
        else:
            relationship = Relationship(source_node_id=self.last_instruct, target_node_id=instruction.id_, label='instruction')
            self.graph.add_node(instruction)
            self.graph.add_relationship(relationship)
            self.last_instruct = instruction.id_
        self.instruct_len += 1

        if tools:
            if isinstance(tools, Tool):
                tools = [tools]
            for tool in tools:
                relationship = Relationship(source_node_id=tool.id_, target_node_id=self.last_instruct, label='tool')
                self.graph.add_node(tool)
                self.graph.add_relationship(relationship)

    def pop_instruction(self):
        if self.graph.is_empty():
            return
        elif self.instruct_len == 1:
            self.graph.clear()
            self.last_instruct = None
            self.first_instruct = None
            self.instruct_len -= 1
        else:
            relationships = self.get_node_relationships(self.graph.nodes[self.last_instruct], out_edge=False)
            prev_instruct = None
            for r in relationships:
                if r.label != 'instruction':
                    self.graph.remove_node(self.graph.nodes[r.source_node_id])
                else:
                    prev_instruct = r.source_node_id

            self.graph.remove_node(self.graph.nodes[self.last_instruct])
            self.last_instruct = prev_instruct
            self.instruct_len -= 1

    def get_instruction_node(self, node_id):
        return self.graph.nodes[node_id]

    def get_tools(self, instruct_node: Instruction):
        relationships = self.get_node_relationships(instruct_node, out_edge=False, labels=['tool'])
        tools = []
        for r in relationships:
            tool = self.graph.nodes[r.source_node_id]
            tools.append(tool)
        return tools


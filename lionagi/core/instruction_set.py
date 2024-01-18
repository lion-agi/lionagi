from typing import List, Union
from ..schema import Tool
from ..structures import Relationship, Structure
from .messages import Instruction


# dynamically structured preconfigured instructions
class InstructionSet(Structure):
    """
    Represents a set of instructions and their relationships to tools.

    Attributes:
        last_instruct (Optional[str]): ID of the last instruction added.
        first_instruct (Optional[str]): ID of the first instruction added.
        instruct_len (int): The total number of instructions.

    Example usage:
        >>> instruction_set = InstructionSet()
        >>> instruction = Instruction(...)
        >>> tool = Tool(...)
        >>> instruction_set.add_instruction(instruction)
        >>> instruction_set.add_instruction(instruction, tools=tool)
        >>> instruction_set.pop_instruction()
        >>> instruction_node = instruction_set.get_instruction_by_id('node_id')
        >>> next_instruction = instruction_set.get_next_instruction(instruction_node)
        >>> tools = instruction_set.get_associated_tools(instruction_node)
    """
    last_instruct: str = None
    first_instruct: str = None
    instruct_len: int = 0

    def add_instruction(self, instruction: Instruction, tools: Union[Tool, List[Tool]] = None):
        """
        Add an instruction to the instruction set.

        Args:
            instruction (Instruction): The instruction to add.
            tools (Union[Tool, List[Tool]], optional): The tool or list of tools related to the instruction.

        Example usage:
            >>> instruction_set = InstructionSet()
            >>> instruction = Instruction(...)
            >>> tool = Tool(...)
            >>> instruction_set.push_instruction(instruction)
            >>> instruction_set.push_instruction(instruction, tools=tool)
        """

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
        """
        Remove the last instruction from the instruction set.

        Example usage:
            >>> instruction_set = InstructionSet()
            >>> instruction_set.pop_instruction()
        """
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

    def get_instruction_by_id(self, node_id):
        """
        Retrieve an instruction by its ID.

        Args:
            node_id (str): The ID of the instruction node.

        Returns:
            Instruction: The instruction node associated with the given ID.

        Example usage:
            >>> instruction_set = InstructionSet()
            >>> instruction_node = instruction_set.get_instruction_by_id('node_id')
        """
        return self.graph.nodes[node_id]

    def get_next_instruction(self, instruct_node: Instruction):
        """
        Retrieve the next instruction following the given instruction node.

        Args:
            instruct_node (Instruction): The current instruction node.

        Returns:
            Optional[Instruction]: The next instruction node in the sequence, if it exists.

        Example usage:
            >>> instruction_set = InstructionSet()
            >>> current_node = Instruction(...)
            >>> next_node = instruction_set.get_next_instruction(current_node)
        """
        relationship = self.get_node_relationships(instruct_node)
        if relationship:
            return self.graph.nodes[relationship[0].target_node_id]

    def get_tools(self, instruct_node: Instruction):
        """
        Retrieve the tools associated with a given instruction node.

        Args:
            instruct_node (Instruction): The instruction node to retrieve tools for.

        Returns:
            List[Tool]: The tools associated with the instruction node.

        Example usage:
            >>> instruction_set = InstructionSet()
            >>> instruction_node = Instruction(...)
            >>> tools = instruction_set.get_tools(instruction_node)
        """
        relationships = self.get_node_relationships(instruct_node, out_edge=False, labels=['tool'])
        tools = []
        for r in relationships:
            tool = self.graph.nodes[r.source_node_id]
            tools.append(tool)
        return tools

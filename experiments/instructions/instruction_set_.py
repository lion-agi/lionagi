from typing import List, Union
from lionagi.core.message.schema import Tool
from lionagi.core.work.structure_executor import ExecutableStructure
from lionagi.core.generic.base.edge import Edge
from lionagi.core.session import Instruction


class InstructionSet(ExecutableStructure):
    """
    Represents a set of instructions and their edge to tools.

    Attributes:
        last_instruct (Optional[str]): ID of the last instruction added.
        first_instruct (Optional[str]): ID of the first instruction added.
        instruct_len (int): The total number of instructions.

    Example usage:
        >>> instruction_set = InstructionSet()
        >>> instruction = BaseInstruction(...)
        >>> tools = Tool(...)
        >>> instruction_set.add_instruction(instruction)
        >>> instruction_set.add_instruction(instruction, tools=tools)
        >>> instruction_set.pop_instruction()
        >>> instruction_node = instruction_set.get_instruction_by_id('node_id')
        >>> next_instruction = instruction_set.get_next_instruction(instruction_node)
        >>> tools = instruction_set.get_associated_tools(instruction_node)
    """
    last_instruct: str = None
    first_instruct: str = None
    instruct_len: int = 0

    def add_instruction(self, instruction: Instruction,
                        tools: Union[Tool, List[Tool]] = None):
        """
        Add an instruction to the instruction set.

        Args:
            instruction (BaseInstruction): The instruction to add.
            tools (Union[Tool, List[Tool]], optional): The tools or list of tools related to the instruction.

        Example usage:
            >>> instruction_set = InstructionSet()
            >>> instruction = BaseInstruction(...)
            >>> tools = Tool(...)
            >>> instruction_set.push_instruction(instruction)
            >>> instruction_set.push_instruction(instruction, tools=tools)
        """

        if self.internal.is_empty():
            self.internal.add_structure_node(instruction)
            self.last_instruct = instruction.id_
            self.first_instruct = instruction.id_
        else:
            relationship = Edge(source_node_id=self.last_instruct,
                                        target_node_id=instruction.id_,
                                        label='instruction')
            self.internal.add_structure_node(instruction)
            self.internal.add_relationship(relationship)
            self.last_instruct = instruction.id_
        self.instruct_len += 1

        if tools:
            if isinstance(tools, Tool):
                tools = [tools]
            for tool in tools:
                relationship = Edge(source_node_id=tool.id_,
                                            target_node_id=self.last_instruct,
                                            label='tools')
                self.internal.add_structure_node(tool)
                self.internal.add_relationship(relationship)

    def pop_instruction(self):
        """
        Remove the last instruction from the instruction set.

        Example usage:
            >>> instruction_set = InstructionSet()
            >>> instruction_set.pop_instruction()
        """
        if self.internal.is_empty():
            return
        elif self.instruct_len == 1:
            self.internal.clear()
            self.last_instruct = None
            self.first_instruct = None
            self.instruct_len -= 1
        else:
            relationships = self.get_node_edges(
                self.internal.structure_nodes[self.last_instruct], out_edge=False)
            prev_instruct = None
            for r in relationships:
                if r.label != 'instruction':
                    self.internal.remove_node(self.internal.structure_nodes[r.source_node_id])
                else:
                    prev_instruct = r.source_node_id

            self.internal.remove_node(self.internal.structure_nodes[self.last_instruct])
            self.last_instruct = prev_instruct
            self.instruct_len -= 1

    def get_instruction_by_id(self, node_id):
        """
        Retrieve an instruction by its ID.

        Args:
            node_id (str): The ID of the instruction node.

        Returns:
            BaseInstruction: The instruction node associated with the given ID.

        Example usage:
            >>> instruction_set = InstructionSet()
            >>> instruction_node = instruction_set.get_instruction_by_id('node_id')
        """
        return self.internal.structure_nodes[node_id]

    def get_next_instruction(self, instruct_node: Instruction):
        """
        Retrieve the next instruction following the given instruction node.

        Args:
            instruct_node (BaseInstruction): The current instruction node.

        Returns:
            Optional[BaseInstruction]: The next instruction node in the sequence, if it exists.

        Example usage:
            >>> instruction_set = InstructionSet()
            >>> current_node = BaseInstruction(...)
            >>> next_node = instruction_set.get_next_instruction(current_node)
        """
        relationship = self.get_node_edges(instruct_node)
        if relationship:
            return self.internal.structure_nodes[relationship[0].target_node_id]

    def get_tools(self, instruct_node: Instruction):
        """
        Retrieve the tools associated with a given instruction node.

        Args:
            instruct_node (BaseInstruction): The instruction node to retrieve tools for.

        Returns:
            List[Tool]: The tools associated with the instruction node.

        Example usage:
            >>> instruction_set = InstructionSet()
            >>> instruction_node = BaseInstruction(...)
            >>> tools = instruction_set.get_tools(instruction_node)
        """
        relationships = self.get_node_edges(instruct_node, out_edge=False,
                                                    labels=['tools'])
        tools = []
        for r in relationships:
            tool = self.internal.structure_nodes[r.source_node_id]
            tools.append(tool)
        return tools

# # new methods
#     def insert_instruction(self, index: int, instruction: BaseInstruction, tools: Union[Tool, List[Tool]] = None):
#         """
#         Insert an instruction at a specified index in the instruction set.
#
#         Args:
#             index (int): The index to insert the instruction at.
#             instruction (BaseInstruction): The instruction to insert.
#             tools (Union[Tool, List[Tool]], optional): The tools or list of tools related to the instruction.
#         """
#         if index < 0 or index > self.instruct_len:
#             raise IndexError("Index out of bounds.")
#
#         if index == self.instruct_len:
#             self.add_instruction(instruction, tools)
#             return
#
#         # Adjust edge and insert the new instruction
#         current_node = self.first_instruct
#         for _ in range(index):
#             next_node = self.get_next_instruction(self.graph.nodes[current_node])
#             current_node = next_node.id_
#
#         prev_node = self.graph.get_node_relationships(current_node, out_edge=False)
#         prev_node_id = prev_node[0].source_node_id if prev_node else None
#
#         if prev_node_id:
#             self.graph.remove_relationship_between(prev_node_id, current_node)
#
#         new_rel = Edge(prev_node_id, instruction.id_, 'instruction')
#         self.graph.add_node(instruction)
#         self.graph.add_relationship(new_rel)
#         self.graph.add_relationship(Edge(instruction.id_, current_node, 'instruction'))
#
#         self.instruct_len += 1
#         self._add_tools_to_instruction(instruction, tools)
#
#     def replace_instruction(self, instruction_id: str, new_instruction: BaseInstruction):
#         """
#         Replace an existing instruction with a new instruction.
#
#         Args:
#             instruction_id (str): The ID of the instruction to replace.
#             new_instruction (BaseInstruction): The new instruction to replace with.
#         """
#         if not self.graph.node_exist(instruction_id):
#             return False
#
#         prev_rel = self.graph.get_node_relationships(instruction_id, out_edge=False)
#         next_rel = self.graph.get_node_relationships(instruction_id)
#
#         if prev_rel:
#             self.graph.remove_relationship(prev_rel[0])
#             self.graph.add_relationship(Edge(prev_rel[0].source_node_id, new_instruction.id_, 'instruction'))
#
#         if next_rel:
#             self.graph.remove_relationship(next_rel[0])
#             self.graph.add_relationship(Edge(new_instruction.id_, next_rel[0].target_node_id, 'instruction'))
#
#         self.graph.replace_node(instruction_id, new_instruction)
#         return True
#
#     def move_instruction(self, instruction_id: str, new_index: int):
#         """
#         Move an instruction to a new index within the instruction set.
#
#         Args:
#             instruction_id (str): The ID of the instruction to move.
#             new_index (int): The new index to move the instruction to.
#         """
#         if not self.graph.node_exist(instruction_id) or new_index < 0 or new_index >= self.instruct_len:
#             return False
#
#         # Remove the instruction from its current position
#         removed_instruction = self.graph.remove_node(instruction_id)
#         if removed_instruction:
#             # Reinsert at the new position
#             self.insert_instruction(new_index, removed_instruction)
#             return True
#         return False
#
#     def clear_instructions(self):
#         """
#         Clear all instructions from the instruction set.
#         """
#         self.graph.clear()
#         self.last_instruct = None
#         self.first_instruct = None
#         self.instruct_len = 0
#
#     def _add_tools_to_instruction(self, instruction: BaseInstruction, tools: Union[Tool, List[Tool]]):
#         """
#         Helper method to add tools to an instruction.
#
#         Args:
#             instruction (BaseInstruction): The instruction to associate tools with.
#             tools (Union[Tool, List[Tool]]): The tools or list of tools to associate.
#         """
#         if tools:
#             if isinstance(tools, Tool):
#                 tools = [tools]
#             for tools in tools:
#                 edge = Edge(source_node_id=tools.id_, target_node_id=instruction.id_, label='tools')
#                 self.graph.add_node(tools)
#                 self.graph.add_relationship(edge)
#
#
#     def get_previous_instruction(self, instruct_node: BaseInstruction):
#         """
#         Retrieve the previous instruction before the given instruction node.
#
#         Args:
#             instruct_node (BaseInstruction): The current instruction node.
#
#         Returns:
#             Optional[BaseInstruction]: The previous instruction node, if it exists.
#
#         Example usage:
#             >>> instruction_set = InstructionSet()
#             >>> current_node = BaseInstruction(...)
#             >>> prev_node = instruction_set.get_previous_instruction(current_node)
#         """
#         edge = self.get_node_relationships(instruct_node, out_edge=False)
#         if edge:
#             return self.graph.nodes[edge[0].source_node_id]
#
#     def get_all_instructions(self):
#         """
#         Retrieve all instructions in the set.
#
#         Returns:
#             List[BaseInstruction]: List of all instructions in the set.
#
#         Example usage:
#             >>> instruction_set = InstructionSet()
#             >>> all_instructions = instruction_set.get_all_instructions()
#         """
#         instructions = []
#         current_node_id = self.first_instruct
#         while current_node_id:
#             current_node = self.graph.nodes[current_node_id]
#             instructions.append(current_node)
#             next_rel = self.get_node_relationships(current_node)
#             current_node_id = next_rel[0].target_node_id if next_rel else None
#         return instructions
#
#     def find_instructions_by_label(self, label: str):
#         """
#         Find all instructions that have a specific label.
#
#         Args:
#             label (str): The label to search for in instructions.
#
#         Returns:
#             List[BaseInstruction]: List of instructions that have the specified label.
#
#         Example usage:
#             >>> instruction_set = InstructionSet()
#             >>> specific_instructions = instruction_set.find_instructions_by_label('label_name')
#         """
#         return [node for node in self.graph.nodes.values() if isinstance(node, BaseInstruction) and node.label == label]

# def remove_instruction_by_id(self, instruction_id: str):
#     """
#     Remove an instruction from the set by its ID.
#
#     Args:
#         instruction_id (str): The ID of the instruction to remove.
#
#     Returns:
#         bool: True if the instruction was removed, False otherwise.
#
#     Example usage:
#         >>> instruction_set = InstructionSet()
#         >>> instruction_set.remove_instruction_by_id('instruction_id')
#     """
#     if instruction_id not in self.graph.nodes:
#         return False
#     to_remove = self.graph.nodes[instruction_id]
#     prev_rel = self.graph.get_node_relationships(instruction_id, out_edge=False)
#     next_rel = self.graph.get_node_relationships(instruction_id)
#
#     if prev_rel and next_rel:
#         self.graph.add_relationship(Edge(prev_rel[0].source_node_id, next_rel[0].target_node_id, 'instruction'))
#
#     self.graph.remove_node(to_remove)
#     self.instruct_len -= 1
#     if instruction_id == self.first_instruct:
#         self.first_instruct = next_rel[0].target_node_id if next_rel else None
#     if instruction_id == self.last_instruct:
#         self.last_instruct = prev_rel[0].source_node_id if prev_rel else None
#
#     return True

# def add_instruction_set(self, name: str, instruction_set: InstructionSet) -> None:
#     """
#     Adds an instruction set to the current active branch.
#
#     Args:
#         name (str): The name of the instruction set.
#         instruction_set (InstructionSet): The instruction set to add.
#     """
#     self.default_branch.add_instruction_set(name, instruction_set)
#
# def remove_instruction_set(self, name: str) -> bool:
#     """
#     Removes an instruction set from the current active branch.
#
#     Args:
#         name (str): The name of the instruction set to remove.
#
#     Returns:
#         bool: True if the instruction set is removed, False otherwise.
#     """
#     return self.default_branch.remove_instruction_set(name)
